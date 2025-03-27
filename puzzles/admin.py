from django.contrib import admin
from django.urls import reverse

from puzzles.models import (
    AnswerSubmission,
    CannedHint,
    Erratum,
    ExtraGuessGrant,
    Hint,
    HintClaimer,
    Puzzle,
    PuzzleMessage,
    PuzzleUnlock,
    Round,
    Survey,
    Team,
    TeamMember,
)


class RoundAdmin(admin.ModelAdmin):
    def view_on_site(self, obj):
        return reverse("round", args=(obj.slug,))

    ordering = ("order",)
    list_display = ("name", "slug", "order")


class PuzzleMessageInline(admin.TabularInline):
    model = PuzzleMessage


class CannedHintInline(admin.TabularInline):
    model = CannedHint


class PuzzleAdmin(admin.ModelAdmin):
    def view_on_site(self, obj):
        return reverse("puzzle", args=(obj.slug,))

    inlines = [PuzzleMessageInline, CannedHintInline]
    ordering = ("round__order", "order")
    list_display = (
        "name",
        "slug",
        "round",
        "order",
        "unlock_hours",
        "unlock_global",
        "unlock_local",
        "is_meta",
        "emoji",
    )
    list_filter = ("round", "is_meta")


class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "team")
    list_filter = ("team",)
    search_fields = ("name", "email")


class TeamMemberInline(admin.TabularInline):
    model = TeamMember


class TeamAdmin(admin.ModelAdmin):
    inlines = [TeamMemberInline]

    def view_on_site(self, obj):
        return reverse("team", args=(obj.team_name,))

    # You can't sort by this column but meh.
    def is_prerelease_testsolver_short(self, obj):
        return obj.is_prerelease_testsolver

    is_prerelease_testsolver_short.short_description = "Prerel.?"
    is_prerelease_testsolver_short.boolean = True

    ordering = ("team_name",)
    list_display = (
        "team_name",
        "creation_time",
        "is_prerelease_testsolver_short",
        "is_hidden",
    )
    list_filter = ("is_prerelease_testsolver", "is_hidden")
    search_fields = ("team_name",)
    readonly_fields = ("id",)


class PuzzleUnlockAdmin(admin.ModelAdmin):
    list_display = ("team", "puzzle", "unlock_datetime")
    list_filter = ("puzzle", "puzzle__round", "team")


class AnswerSubmissionAdmin(admin.ModelAdmin):
    list_display = (
        "team",
        "puzzle",
        "submitted_answer",
        "submitted_datetime",
        "is_correct",
        "is_message",
        "used_free_answer",
    )
    list_filter = (
        "is_correct",
        "is_message",
        "used_free_answer",
        "puzzle",
        "puzzle__round",
        "team",
    )
    search_fields = ("submitted_answer",)


class ExtraGuessGrantAdmin(admin.ModelAdmin):
    list_display = ("team", "puzzle", "extra_guesses")
    list_filter = ("puzzle", "puzzle__round", "team")


class ErratumAdmin(admin.ModelAdmin):
    list_display = ("puzzle", "subject", "timestamp", "published")
    list_filter = ("puzzle", "puzzle__round", "published")
    search_fields = ("puzzle", "subject", "update_text", "puzzle_text")


class SurveyAdmin(admin.ModelAdmin):
    list_display = ("team", "puzzle", "submitted_datetime")
    list_filter = ("puzzle", "puzzle__round", "team")
    search_fields = ("comments",)


class HintAdmin(admin.ModelAdmin):
    def view_on_site(self, obj):
        return reverse("hint", args=(obj.id,))

    list_display = (
        "team",
        "puzzle",
        "claimed_by",
        "status",
        "is_followup",
        "submitted_datetime",
        "claimed_datetime",
        "answered_datetime",
    )
    list_filter = ("status", "puzzle", "puzzle__round", "team", "claimed_by")
    search_fields = ("hint_question", "response")


class HintClaimerAdmin(admin.ModelAdmin):
    list_display = ("display_name", "username", "discord_user_id")
    search_fields = ("display_name", "username")


class CannedHintAdmin(admin.ModelAdmin):
    list_display = (
        "puzzle",
        "order",
        "description",
        "keywords",
        "content",
    )
    list_filter = ("puzzle",)
    search_fields = ("content",)


admin.site.register(Round, RoundAdmin)
admin.site.register(Puzzle, PuzzleAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamMember, TeamMemberAdmin)
admin.site.register(PuzzleUnlock, PuzzleUnlockAdmin)
admin.site.register(AnswerSubmission, AnswerSubmissionAdmin)
admin.site.register(ExtraGuessGrant, ExtraGuessGrantAdmin)
admin.site.register(Erratum, ErratumAdmin)
admin.site.register(Survey, SurveyAdmin)
admin.site.register(Hint, HintAdmin)
admin.site.register(HintClaimer, HintClaimerAdmin)
admin.site.register(CannedHint, CannedHintAdmin)
