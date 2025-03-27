import re
import unicodedata

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.utils.translation import gettext as _

from puzzles.discord import DISCORD_IMAGE_BASE_URL, DiscordClient
from puzzles.models import (
    Hint,
    HintClaimer,
    Survey,
    Team,
    TeamMember,
)


def looks_spammy(s):
    # do not allow names that are only space or control characters
    if all(unicodedata.category(c).startswith(("Z", "C")) for c in s):
        return True
    return re.search("https?://", s, re.IGNORECASE) is not None


class RegisterForm(forms.Form):
    team_id = forms.CharField(
        label=_("Team Username"),
        max_length=100,
        help_text=(
            _(
                "This is the private username your team will use when logging in. "
                "It should be short and not contain special characters."
            )
        ),
    )
    team_name = forms.CharField(
        label=_("Team Name"),
        max_length=200,
        help_text=(
            _("This is how your team name will appear on the public leaderboard.")
        ),
    )
    password = forms.CharField(
        label=_("Team Password"),
        widget=forms.PasswordInput,
        help_text=_("You’ll probably share this with your team."),
    )
    password2 = forms.CharField(
        label=_("Retype Password"),
        widget=forms.PasswordInput,
    )

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = self.cleaned_data

        team_id = cleaned_data.get("team_id")
        password = cleaned_data.get("password")
        password2 = cleaned_data.get("password2")
        team_name = cleaned_data.get("team_name")

        if not team_name or looks_spammy(team_name):
            raise forms.ValidationError(_("That public team name isn’t allowed."))

        if password != password2:
            raise forms.ValidationError(_("Passwords don’t match."))

        if User.objects.filter(username=team_id).exists():
            raise forms.ValidationError(
                _("That login username has already been taken by a different team.")
            )

        if Team.objects.filter(team_name=team_name).exists():
            raise forms.ValidationError(
                _("That public team name has already been taken by a different team.")
            )

        return cleaned_data


def validate_team_member_email_unique(email):
    if TeamMember.objects.filter(email=email).exists():
        raise forms.ValidationError(
            _(
                "Someone with that email is already registered as a member on a "
                "different team."
            )
        )


class TeamMemberForm(forms.Form):
    name = forms.CharField(label=_("Name (required)"), max_length=200)
    email = forms.EmailField(
        label=_("Email (optional)"),
        max_length=200,
        required=False,
        validators=[validate_email, validate_team_member_email_unique],
    )


def validate_team_emails(formset):
    emails = []
    for form in formset.forms:
        name = form.cleaned_data.get("name")
        if not name:
            raise forms.ValidationError(_("All team members must have names."))
        if looks_spammy(name):
            raise forms.ValidationError(_("That team member name isn’t allowed."))
        email = form.cleaned_data.get("email")
        if email:
            emails.append(email)
    if not emails:
        raise forms.ValidationError(_("You must list at least one email address."))
    if len(emails) != len(set(emails)):
        raise forms.ValidationError(_("All team members must have unique emails."))
    return emails


class TeamMemberFormset(forms.BaseFormSet):
    def clean(self):
        if any(self.errors):
            return
        validate_team_emails(self)


class TeamMemberModelFormset(forms.models.BaseModelFormSet):
    def clean(self):
        if any(self.errors):
            return
        emails = validate_team_emails(self)
        if (
            TeamMember.objects.exclude(team=self.data["team"])
            .filter(email__in=emails)
            .exists()
        ):
            raise forms.ValidationError(
                _("One of the emails you listed is already on a different team.")
            )


class SubmitAnswerForm(forms.Form):
    answer = forms.CharField(
        label=_("Enter your guess:"),
        max_length=500,
        widget=forms.TextInput(attrs={"autofocus": True}),
    )


class RequestHintForm(forms.Form):
    hint_question = forms.CharField(
        label=(
            _(
                "Describe everything you’ve tried on this puzzle. We will "
                "provide a hint to help you move forward. The more detail you "
                "provide, the less likely it is that we’ll tell you "
                "something you already know."
            )
        ),
        widget=forms.Textarea,
    )

    def __init__(self, team, *args, **kwargs):
        super().__init__(*args, **kwargs)
        notif_choices = [("all", _("Everyone")), ("none", _("No one"))]
        notif_choices.extend(team.get_emails(with_names=True))
        self.fields["notify_emails"] = forms.ChoiceField(
            label=_("When the hint is answered, send an email to:"),
            choices=notif_choices,
        )


class HintStatusWidget(forms.Select):
    def get_context(self, name, value, attrs):
        self.choices = []
        for option, desc in Hint.STATUSES:
            if option == Hint.NO_RESPONSE:
                if value != Hint.NO_RESPONSE:
                    continue
            elif option == Hint.ANSWERED:
                if value == Hint.OBSOLETE:
                    continue
                if self.is_followup:
                    desc += _(" (as followup)")  # noqa: PLW2901
            elif option == Hint.REFUNDED:
                if value == Hint.OBSOLETE:
                    continue
                if self.is_followup:
                    desc += _(" (thread closed)")  # noqa: PLW2901
            elif option == Hint.OBSOLETE:
                if value != Hint.OBSOLETE:
                    continue
            self.choices.append((option, desc))
        if value == Hint.NO_RESPONSE:
            value = Hint.ANSWERED
            attrs["style"] = "background-color: #ff3"
        return super().get_context(name, value, attrs)


class HintClaimerForm(forms.models.ModelForm):
    display_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(
            attrs={"list": "display_name_list"}
        ),  # Attach to datalist
        label="Select or enter a display name",
    )

    class Meta:
        model = HintClaimer
        fields = ["display_name"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fetch existing display names for the datalist
        existing_names = HintClaimer.objects.values_list(
            "display_name", flat=True
        ).distinct()
        self.existing_names = list(existing_names)  # Store for template rendering

    def clean_display_name(self):
        display_name = self.cleaned_data.get("display_name")
        guild_id = settings.DISCORD_GUILD_ID

        if not display_name:
            msg = "Display name is required."
            raise forms.ValidationError(msg)

        try:
            users = DiscordClient.search_user(guild_id, display_name)
        except Exception as e:
            msg = "Internal error."
            raise forms.ValidationError(msg) from e

        if not users:
            msg = "User not found in hunt management Discord server"
            raise forms.ValidationError(msg)

        guild_member = users[0]

        user_id = guild_member["user"]["id"]

        display_name = (
            guild_member["nick"]
            or guild_member["user"]["global_name"]
            or guild_member["user"]["username"]
        )
        self.cleaned_data["discord_user_id"] = user_id
        self.cleaned_data["username"] = guild_member["user"]["username"]

        # Guild-specific avatar
        if avatar_hash := guild_member["avatar"]:
            avatar_url = f"{DISCORD_IMAGE_BASE_URL}/guilds/{guild_id}/users/{user_id}/avatars/{avatar_hash}.png"
        # Global avatar
        elif avatar_hash := guild_member["user"]["avatar"]:
            avatar_url = f"{DISCORD_IMAGE_BASE_URL}/avatars/{user_id}/{avatar_hash}.png"
        # Default avatar
        else:
            # Don't need to handle discriminators
            avatar_idx = (int(user_id) >> 22) % 6
            avatar_url = f"{DISCORD_IMAGE_BASE_URL}/embed/avatars/{avatar_idx}.png"

        self.cleaned_data["avatar_url"] = avatar_url

        return display_name

    def save(self, commit=True):
        display_name = self.cleaned_data.get("display_name")

        instance = HintClaimer.objects.filter(display_name=display_name).first()
        if not instance:
            instance = super().save(commit=False)
            instance.display_name = display_name

        instance.discord_user_id = self.cleaned_data["discord_user_id"]
        instance.username = self.cleaned_data["username"]
        instance.avatar_url = self.cleaned_data["avatar_url"]

        if commit:
            instance.save()

        return instance


class AnswerHintForm(forms.ModelForm):
    class Meta:
        model = Hint
        fields = ("response", "status")
        widgets = {"status": HintStatusWidget}


class SurveyForm(forms.ModelForm):
    class Meta:
        model = Survey
        fields = ("fun", "difficulty", "comments")


# This form is a customization of forms.PasswordResetForm
class PasswordResetForm(forms.Form):
    team_id = forms.CharField(label=_("Team Username"), max_length=100)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data is None:
            cleaned_data = self.cleaned_data
        team_id = cleaned_data.get("team_id")
        if team_id is None:
            raise forms.ValidationError(_("That username doesn’t exist."))
        team = Team.objects.filter(user__username=team_id).first()
        if team is None:
            raise forms.ValidationError(_("That username doesn’t exist."))
        cleaned_data["team"] = team
        return cleaned_data
