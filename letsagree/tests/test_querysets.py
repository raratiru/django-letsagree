#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import sqlite3

from collections import defaultdict
from django.conf import settings
from letsagree.models import Term

pytestmark = pytest.mark.django_db


@pytest.mark.skipif(
    all(
        (
            float(".".join(sqlite3.sqlite_version.split(".")[:2])) < 3.25,
            "sqlite3" in settings.DATABASES["default"]["ENGINE"],
        )
    ),
    reason="Window Function is not supported in this SQLite version",
)
def test_pending(queries, django_assert_num_queries):
    setup = queries(terms_agreed=False)
    # The user is member of 3 groups
    assert setup.request.user.groups.count() == 3
    terms_per_group = setup.request.user.groups.values_list("id", "terms")
    d = defaultdict(list)
    for k, v in d:
        terms_per_group[k].append(v)
    # Each group is associated with a newer and an older version of terms
    for v in terms_per_group.values():
        assert len(v) == 2
    # The user has not agreed to any term
    assert setup.request.user.agreed_terms.count() == 0
    # The maximum number of terms that the user would have agreed is 6:
    # ( 3 missed and 3 pending )
    assert setup.request.user.groups.filter(terms__users_agreed__id=None).count() == 6
    # The user will be asked to agree on the most recent version of the terms
    # of each group he belongs to.
    with django_assert_num_queries(1):
        assert Term.objects.get_pending_terms(setup.request.user).count() == 3


@pytest.mark.skipif(
    all(
        (
            float(".".join(sqlite3.sqlite_version.split(".")[:2])) < 3.25,
            "sqlite3" in settings.DATABASES["default"]["ENGINE"],
        )
    ),
    reason="Window Function is not supported in this SQLite version",
)
def test_agreed(queries, django_assert_num_queries):
    setup = queries(terms_agreed=True)
    # The user is member of 1 grroup
    assert setup.request.user.groups.count() == 1
    terms_per_group = setup.request.user.groups.values_list("id", "terms")
    d = defaultdict(list)
    for k, v in d:
        terms_per_group[k].append(v)
    # Each group is associated with a newer and an older version of terms
    for v in terms_per_group.values():
        assert len(v) == 2
    # The user has agreed to one term
    assert setup.request.user.agreed_terms.count() == 1
    # The terms that the user would have agreed but missed is 1:
    assert setup.request.user.groups.filter(terms__users_agreed__id=None).count() == 1
    # The user will not be asked to agree on any term
    with django_assert_num_queries(1):
        assert Term.objects.get_pending_terms(setup.request.user).count() == 0
    # The query of agreed terms returns 1
    with django_assert_num_queries(1):
        assert Term.objects.get_signed_agreements(setup.request.user).count() == 1


@pytest.mark.skipif(
    all(
        (
            float(".".join(sqlite3.sqlite_version.split(".")[:2])) < 3.25,
            "sqlite3" in settings.DATABASES["default"]["ENGINE"],
        )
    ),
    reason="Window Function is not supported in this SQLite version",
)
def test_agreed_pending(queries, django_assert_num_queries):
    setup = queries(terms_agreed="AgreedAndPending")
    # The user is member of 2 grroup
    assert setup.request.user.groups.count() == 2
    terms_per_group = setup.request.user.groups.values_list("id", "terms")
    d = defaultdict(list)
    for k, v in d:
        terms_per_group[k].append(v)
    # Each group is associated with a newer and an older version of terms
    for v in terms_per_group.values():
        assert len(v) == 2
    # The user has agreed to one term
    assert setup.request.user.agreed_terms.count() == 1
    # The terms that the user would have agreed but missed are 3:
    assert setup.request.user.groups.filter(terms__users_agreed__id=None).count() == 3
    # The user will be asked to agree on 1 term
    with django_assert_num_queries(1):
        assert Term.objects.get_pending_terms(setup.request.user).count() == 1
    # The query of agreed terms returns 1
    with django_assert_num_queries(1):
        assert Term.objects.get_signed_agreements(setup.request.user).count() == 1
