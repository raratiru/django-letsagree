#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sqlite3

from letsagree.middleware import LetsAgreeMiddleware
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse

pytestmark = pytest.mark.django_db


def test_middleware_init():
    my_middleware = LetsAgreeMiddleware("response")
    assert my_middleware.get_response == "response"


@pytest.mark.skipif(
    all(
        (
            float(".".join(sqlite3.sqlite_version.split(".")[:2])) < 3.25,
            "sqlite3" in settings.DATABASES["default"]["ENGINE"],
        )
    ),
    reason="Window Function is not supported in this SQLite version",
)
@pytest.mark.parametrize(
    "cache_enabled,terms_agreed,request_url,response_count,queries_count",
    [
        # Always 0 database queries
        (False, "AnonymousUser", "/", 1, 0),
        (True, "AnonymousUser", "/", 1, 0),
        (False, False, reverse("letsagree:pending"), 1, 0),  # User can agree!
        (False, False, reverse("admin:logout"), 1, 0),  # User can logout
        (False, False, reverse("admin:logout"), 1, 0),  # User can logout
        (
            False,
            False,
            reverse("admin:app_list", args=("letsagree",)),
            1,
            0,
        ),  # User can visit app
        # Max 1 database query
        (False, False, reverse("admin:letsagree_term_add"), 0, 1),  # User cannot add
        (False, True, "/", 1, 1),
        (True, True, "/", 1, 1),
        #    Redirect to accept the terms -> response_count = 0
        (False, False, "/", 0, 1),
        (True, False, "/", 0, 1),
        (  # Edge case: Avoid recursion with the 'next' parameter.
            False,
            False,
            "{0}/?next={0}".format(reverse("letsagree:pending")),
            0,
            1,
        ),
    ],
)
def test_middleware(
    queries,
    settings,
    django_assert_num_queries,
    queries_count,
    request_url,
    response_count,
    cache_enabled,
    terms_agreed,
):
    """
    Anonymous user: Always 0 database hits expected.
    Logged in user:
        * Always 1 database hit expected
        * If cache is enabled, from the second middleware call onwards,
          0 database hits expected.
    0 response count = the middleware redirects in order to accept terms.
    1 response count = the middleware calls get_response() and the reqest
    proceeds according to the user's whish.
    """
    settings.LETSAGREE_CACHE = cache_enabled
    settings.LETSAGREE_LOGOUT_APP_NAME = "admin"
    setup = queries(terms_agreed, request_url)
    cache.delete("letsagree-{0}".format(setup.request.user.id))
    with django_assert_num_queries(queries_count):
        middleware = LetsAgreeMiddleware(setup.response)
        middleware(setup.request)
        assert setup.response.call_count == response_count
        setup.response.reset_mock()
    if cache_enabled:
        with django_assert_num_queries(0):
            middleware = LetsAgreeMiddleware(setup.response)
            middleware(setup.request)
            assert setup.response.call_count == response_count
            setup.response.reset_mock()
