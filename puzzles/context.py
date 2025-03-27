# Roughly speaking, this module is most important for implementing "global
# variables" that are available in every template with the Django feature of
# "context processors". But it also does some stuff with caching computed
# properties of teams (the caching is only within a single request (?)). See
# https://docs.djangoproject.com/en/3.1/ref/templates/api/#using-requestcontext
import datetime
import inspect
import types
from functools import cached_property

from django.conf import settings
from django.utils import timezone

from puzzles import hunt_config, models
from puzzles.hunt_config import (
    HUNT_CLOSE_TIME,
    HUNT_END_TIME,
    HUNT_START_TIME,
    META_META_SLUG,
)
from puzzles.shortcuts import get_shortcuts


def context_middleware(get_response):
    def middleware(request):
        request.context = Context(request)
        return get_response(request)

    return middleware


# A context processor takes a request and returns a dictionary of (key: value)s
# to merge into the request's context.
def context_processor(request):
    def thunk(name):
        return lambda: getattr(request.context, name)

    return {name: thunk(name) for name in request.context._cached_names}


# Construct a get/set property from a name and a function to compute a value.
# Doing this with name="foo" causes accesses to self.foo to call fn and cache
# the result.
def wrap_cacheable(name, fn):
    def fget(self):
        if not hasattr(self, "_cache"):
            self._cache = {}
        if name not in self._cache:
            self._cache[name] = fn(self)
        return self._cache[name]

    def fset(self, value):
        if not hasattr(self, "_cache"):
            self._cache = {}
        self._cache[name] = value

    return property(fget, fset)


# Decorator for a class, like the `Context` class below but also the `Team`
# model, that replaces all non-special methods that take no arguments other
# than `self` with a get/set property as constructed above, and also gather
# their names into the property `_cached_names`.
def context_cache(cls):
    cached_names = []
    for c in (BaseContext, cls):
        for name, fn in c.__dict__.items():
            if (
                not name.startswith("__")  # not special
                and isinstance(fn, types.FunctionType)  # method
                and (
                    inspect.getfullargspec(fn).args == ["self"]  # only self
                    or inspect.getfullargspec(fn).args == ["self", "__v"]
                )
            ):
                setattr(cls, name, wrap_cacheable(name, fn))
                cached_names.append(name)
            elif isinstance(fn, cached_property):
                setattr(cls, name, fn)
                cached_names.append(name)

    cls._cached_names = tuple(cached_names)
    return cls


# Solely for Team typechecking...
class ContextProps:
    now: datetime.datetime
    start_time: datetime.datetime
    end_time: datetime.datetime
    close_time: datetime.datetime
    hunt_is_prereleased: bool
    hunt_has_started: bool
    hunt_is_over: bool
    hunt_is_closed: bool


# This object is a request-scoped cache containing data calculated for the
# current request. As a motivating example: showing current DEEP in the top
# bar and rendering the puzzles page both need the list of puzzles the current
# team has solved. This object ensures it only needs to be computed once,
# without explicitly having to pass it around from one place to the other.


# There are currently two types of contexts: request Contexts (below) and Team
# models (in models.py). Simple properties that are generally useful to either
# can go in BaseContext. The fact that Teams are contexts enables the above
# caching benefits when calculating things like a team's solves, unlocked
# puzzles, or remaining hints -- whether you're looking at your own logged-in
# team or another team's details page.
class BaseContext:
    team: "models.Team"

    @cached_property
    def now(self):
        return timezone.localtime()

    @cached_property
    def start_time(self) -> datetime.datetime:
        return (
            HUNT_START_TIME - self.team.start_offset if self.team else HUNT_START_TIME
        )

    @cached_property
    def time_since_start(self):
        return self.now - self.start_time

    @cached_property
    def end_time(self):
        return HUNT_END_TIME

    @cached_property
    def close_time(self):
        return HUNT_CLOSE_TIME

    # XXX do NOT name this the same as a field on the actual Team model or
    # you'll silently be unable to update that field because you'll be writing
    # to this instead of the actual model field!
    @cached_property
    def hunt_is_prereleased(self):
        return self.team and self.team.is_prerelease_testsolver

    @cached_property
    def hunt_has_started(self):
        return self.hunt_is_prereleased or self.now >= self.start_time

    @cached_property
    def hunt_has_almost_started(self):
        return self.start_time - self.now < datetime.timedelta(hours=1)

    @cached_property
    def hunt_is_over(self):
        return self.now >= self.end_time

    @cached_property
    def hunt_is_closed(self):
        return self.now >= self.close_time


# Also include the constants from hunt_config.
for key, value in hunt_config.__dict__.items():
    if key.isupper() and key not in (
        "HUNT_START_TIME",
        "HUNT_END_TIME",
        "HUNT_CLOSE_TIME",
    ):
        # Return a lambda to work with the context processor caching
        # only functions, not variables
        setattr(BaseContext, key.lower(), lambda self, __v=value: __v)

# Also include select constants from settings.
for key in ("DOMAIN",):
    value = getattr(settings, key)
    setattr(BaseContext, key.lower(), lambda self, __v=value: __v)


# The properties of a request Context are accessible both from views and from
# templates. If you're adding something with complicated logic, prefer to put
# most of it in a model method and just leave a stub call here.
@context_cache
class Context:
    def __init__(self, request):
        self.request = request

    @cached_property
    def request_user(self):
        return self.request.user

    @cached_property
    def is_superuser(self):
        return self.request_user.is_superuser

    @cached_property
    def team(self):
        return getattr(self.request_user, "team", None)

    @cached_property
    def shortcuts(self):
        return tuple(get_shortcuts(self))

    @cached_property
    def num_hints_remaining(self):
        return self.team.num_hints_remaining if self.team else 0

    @cached_property
    def num_free_answers_remaining(self):
        return self.team.num_free_answers_remaining if self.team else 0

    @cached_property
    def unlocks(self):
        return models.Team.compute_unlocks(self)

    @cached_property
    def all_puzzles(self):
        return tuple(
            models.Puzzle.objects.select_related("round").order_by(
                "round__order", "order"
            )
        )

    @cached_property
    def unclaimed_hints(self):
        return models.Hint.objects.filter(
            status=models.Hint.NO_RESPONSE,
            claimed_by=None,
        ).count()

    @cached_property
    def visible_errata(self):
        return models.Erratum.get_visible_errata(self)

    @cached_property
    def errata_page_visible(self):
        return self.is_superuser or any(
            erratum.updates_text for erratum in self.visible_errata
        )

    @cached_property
    def puzzle(self):
        return None  # set by validate_puzzle

    @cached_property
    def puzzle_answer(self):
        return self.team and self.puzzle and self.team.puzzle_answer(self.puzzle)

    @cached_property
    def guesses_remaining(self):
        return self.team and self.puzzle and self.team.guesses_remaining(self.puzzle)

    @cached_property
    def puzzle_submissions(self):
        return self.team and self.puzzle and self.team.puzzle_submissions(self.puzzle)

    @cached_property
    def round(self):
        return self.puzzle.round if self.puzzle else None

    @cached_property
    def has_finished_hunt(self):
        return (
            any(puzzle.slug == META_META_SLUG for puzzle in self.team.solves.values())
            if self.team
            else False
        )
