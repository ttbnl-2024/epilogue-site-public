import logging
import time
import traceback
from collections import defaultdict

import requests
from django.conf import settings
from django.core.mail import get_connection
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.translation import gettext as _
from huey.contrib.djhuey import db_task, task

from puzzles.discord import DiscordClient, JsonDict
from puzzles.hunt_config import (
    CONTACT_EMAIL,
    HUNT_ORGANIZERS,
    HUNT_TITLE,
    MESSAGING_SENDER_EMAIL,
)

logger = logging.getLogger("puzzles.messaging")


@task()
def dispatch_discord_alert(webhook: str, content: str, username: str = "Django"):
    content = f"<t:{int(time.time())}:t> {content}"

    if (
        settings.IS_TEST or not settings.DISCORD_ENABLED
    ) and not settings.FORCE_LOCAL_DISCORD:
        logger.info(_("(Test) Discord alert:\n") + content)
        return
    logger.info(_("(Real) Discord alert:\n") + content)

    try:
        offset = 0
        while True:
            chunk = content[offset : offset + 2000]
            # possibly chunk but try to preserve whole words
            # inspiration from https://github.com/fixmyrights/discord-bot/issues/11
            if offset + 2000 < len(content):
                reversed_chunk = chunk[::-1]
                length = min(reversed_chunk.find("\n"), reversed_chunk.find(" "))
                chunk = chunk[: 2000 - length]
                offset += 2000 - length
            else:
                offset = len(content)
            requests.post(
                webhook,
                json={
                    "username": username,
                    "content": content,
                    "allowed_mentions": {"parse": []},
                },
            )
            if offset == len(content):
                break
    except Exception:
        logger.error(
            "Failed to post to discord webhook with username %s, content: %s",
            username,
            content,
        )


def build_mail(subject, template, context, recipients, bcc=False):
    if not recipients:
        return None

    # Manually plug in some template variables we know we want
    context["hunt_title"] = HUNT_TITLE
    context["hunt_organizers"] = HUNT_ORGANIZERS
    subject = settings.EMAIL_SUBJECT_PREFIX + subject
    body = render_to_string(template + ".txt", context)
    if settings.IS_TEST:
        logger.info(
            _("Sending mail <{}> to <{}>:\n{}").format(
                subject, ", ".join(recipients), body
            )
        )
        if not settings.FORCE_LOCAL_EMAIL:
            return None
    mail = EmailMultiAlternatives(
        subject=subject,
        body=body,
        from_email=MESSAGING_SENDER_EMAIL,
        alternatives=[(render_to_string(template + ".html", context), "text/html")],
        reply_to=[CONTACT_EMAIL],
    )
    if not bcc:
        mail.to = recipients
    else:
        mail.bcc = recipients
    return mail


# NOTE: we don't have a request available, so this doesn't render with a
# RequestContext, so the magic from our context processor is not available! (We
# maybe could sometimes provide a request, but I don't want to add that
# coupling right now.)


@task()
def send_mail_wrapper(subject, template, context, recipients):
    mail = build_mail(subject, template, context, recipients)
    if not mail:
        return
    try:
        if mail.send() != 1:
            raise RuntimeError(_("Unknown failure???"))
    except Exception:
        logger.error(
            "Could not send mail <%s> to <%s>:\n%s",
            subject,
            ", ".join(recipients),
            traceback.format_exc(),
        )


@task()
def send_mass_mail_wrapper(subject, template, context, recipients):
    message = build_mail(subject, template, context, recipients)

    if not message:
        return

    message.merge_data = {}
    if settings.EMAIL_BACKEND == "anymail.backends.postmark.EmailBackend":
        message.esp_extra = {"MessageStream": "broadcast"}

    try:
        if not message.send():
            raise RuntimeError(_("Unknown failure???"))
    except Exception:
        logger.error(
            "Could not send broadcast mail <%s> to at least one of <%s>:\n%s",
            subject,
            ", ".join(recipients),
            traceback.format_exc(),
        )


@db_task()
def update_hint(hint_id: int):
    from puzzles.messaging import dispatch_general_alert
    from puzzles.models import Hint

    hint = Hint.objects.get(id=hint_id)

    embed: JsonDict = defaultdict(lambda: defaultdict(dict))
    embed["author"]["url"] = hint.full_url()
    if hint.claimed_datetime:
        embed["color"] = 0xDDDDDD
        embed["timestamp"] = hint.claimed_datetime.isoformat()
        embed["author"]["name"] = _("Claimed by {}").format(
            hint.claimed_by.display_name
        )
        embed["author"]["icon_url"] = hint.claimed_by.avatar_url

        debug = _("claimed by {}").format(hint.claimed_by.display_name)
    else:
        embed["color"] = 0xFF00FF
        embed["author"]["name"] = _("U N C L A I M E D")
        claim_url = hint.full_url(claim=True)
        embed["title"] = _("Claim: ") + claim_url
        embed["url"] = claim_url
        debug = "unclaimed"

    if (
        settings.IS_TEST or not settings.DISCORD_ENABLED
    ) and not settings.FORCE_LOCAL_DISCORD:
        message = hint.long_discord_message()
        logger.info(_("Hint, {}: {}\n{}").format(debug, hint, message))
        logger.info(_("Embed: {}").format(embed))
    elif hint.discord_id:
        try:
            DiscordClient.edit_message(
                settings.DISCORD_HINT_CHANNEL_ID, hint.discord_id, {"embeds": [embed]}
            )
        except Exception:
            dispatch_general_alert(
                _("Discord API failure: modify\n{}").format(traceback.format_exc())
            )
            return
    else:
        message = hint.long_discord_message()
        try:
            response = DiscordClient.post_message(
                settings.DISCORD_HINT_CHANNEL_ID,
                {"content": message, "embeds": [embed]},
            )
            discord_id = response["id"]

        except Exception:
            dispatch_general_alert(
                _("Discord API failure: create\n{}").format(traceback.format_exc())
            )
            return

        hint.discord_id = discord_id
        hint.save(update_fields=("discord_id",))


@db_task()
def clear_hint(hint_id: int):
    from puzzles.messaging import dispatch_general_alert
    from puzzles.models import Hint

    hint = Hint.objects.get(id=hint_id)

    if (
        settings.IS_TEST or not settings.DISCORD_ENABLED
    ) and not settings.FORCE_LOCAL_DISCORD:
        logger.info(_("Hint done: {}").format(hint))
    elif hint.discord_id:
        # what DPPH did instead of deleting messages:
        # (nb. I tried to make these colors color-blind friendly)

        embed: JsonDict = defaultdict(lambda: defaultdict(dict))
        if hint.status == hint.ANSWERED:
            embed["color"] = 0xAAFFAA
        elif hint.status == hint.REFUNDED:
            embed["color"] = 0xCC6600

        # nothing for obsolete

        embed["author"]["name"] = _("{} by {}").format(
            hint.get_status_display(), hint.claimed_by.display_name
        )
        embed["author"]["url"] = hint.full_url()
        embed["description"] = hint.response[:250]
        embed["author"]["icon_url"] = hint.claimed_by.avatar_url

        try:
            DiscordClient.edit_message(
                settings.DISCORD_HINT_CHANNEL_ID,
                hint.discord_id,
                {"content": hint.short_discord_message(), "embeds": [embed]},
            )
        except Exception:
            dispatch_general_alert(
                _("Discord API failure: modify\n{}").format(traceback.format_exc())
            )
            return
