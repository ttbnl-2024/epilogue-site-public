import json
import logging

from django.conf import settings
from django.contrib import messages
from django.urls import reverse
from django.utils.translation import gettext as _

from puzzles.tasks import dispatch_discord_alert

logger = logging.getLogger("puzzles.messaging")


# Usernames that the bot will send messages to Discord with when various things
# happen. It's really not important that these are different. It's just for
# flavor.
ALERT_DISCORD_USERNAME = "AlertBot"
CORRECT_SUBMISSION_DISCORD_USERNAME = "WinBot"
PARTIAL_SUBMISSION_DISCORD_USERNAME = "PartialBot"
INCORRECT_SUBMISSION_DISCORD_USERNAME = "FailBot"
FREE_ANSWER_DISCORD_USERNAME = "HelpBot"
VICTORY_DISCORD_USERNAME = "CongratBot"

# Should be Discord webhook URLs that look like
# https://discordapp.com/api/webhooks/(numbers)/(letters)
# From a channel you can create them under Integrations > Webhooks.
# They can be the same webhook if you don't care about keeping them in separate
# channels.

# spoilr-bot-spam
ALERT_WEBHOOK_URL = settings.ALERT_WEBHOOK_URL

# spoilr-guesses
SUBMISSION_WEBHOOK_URL = settings.SUBMISSION_WEBHOOK_URL

# spoilr-free-ans; but unused
FREE_ANSWER_WEBHOOK_URL = settings.FREE_ANSWER_WEBHOOK_URL

# spoilr-congrat
VICTORY_WEBHOOK_URL = settings.VICTORY_WEBHOOK_URL


def dispatch_general_alert(content):
    dispatch_discord_alert(ALERT_WEBHOOK_URL, content, ALERT_DISCORD_USERNAME)


def dispatch_submission_alert(content, status):
    if status == "correct":
        username = CORRECT_SUBMISSION_DISCORD_USERNAME
    elif status == "partial":
        username = PARTIAL_SUBMISSION_DISCORD_USERNAME
    else:
        username = INCORRECT_SUBMISSION_DISCORD_USERNAME
    dispatch_discord_alert(SUBMISSION_WEBHOOK_URL, content, username)


def dispatch_free_answer_alert(content):
    dispatch_discord_alert(
        FREE_ANSWER_WEBHOOK_URL, content, FREE_ANSWER_DISCORD_USERNAME
    )


def dispatch_victory_alert(content):
    dispatch_discord_alert(VICTORY_WEBHOOK_URL, content, VICTORY_DISCORD_USERNAME)


puzzle_logger = logging.getLogger("puzzles.puzzle")


def log_puzzle_info(puzzle, team, content):
    puzzle_logger.info(f"{puzzle}\t{team}\t{content}")


request_logger = logging.getLogger("puzzles.request")


def log_request_middleware(get_response):
    def middleware(request):
        request_logger.info(f"{request.get_full_path()} {request.user}")
        return get_response(request)

    return middleware


def show_unlock_notification(context, unlock):
    data = json.dumps(
        {
            "title": str(unlock.puzzle),
            "text": _("You’ve unlocked a new puzzle!"),
            "link": reverse("puzzle", args=(unlock.puzzle.slug,)),
        }
    )
    messages.info(context.request, data)
