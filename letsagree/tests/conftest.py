#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from collections import namedtuple
from django.contrib.auth.models import AnonymousUser, Permission
from django.db.models import Q
from django.test import RequestFactory
from itertools import tee, chain
from letsagree.tests import factories
from pytest_factoryboy import register
from unittest.mock import Mock


register(factories.GroupFactory)
register(factories.UserFactory)
register(factories.TermFactory)
register(factories.NotaryPublicFactory)


@pytest.fixture
def queries(user_factory, group_factory, term_factory, notary_public_factory):
    """
    This factory creates 3 users and 7 groups.
        * Not agreed: Belongs to 3 groups, has not agreed to any terms
        * Agreed: Belongs to 1 group, has agreed to the terms
        * Belongs to 2 groups, has a greed to 1 of 2 terms
    """
    factory = RequestFactory()
    groups = group_factory.create_batch(7)
    group1, group2 = tee(iter(groups))
    for group in chain.from_iterable(zip(group1, group2)):
        term_factory.create(group_key=group)

    user_not_agreed = user_factory.create(groups=groups[:3])
    user_agreed = user_factory.create(groups=(groups[3],))
    user_agreed_pending = user_factory.create(groups=(groups[4], groups[5]))
    notary_agreed = notary_public_factory.create(
        user_key=user_agreed, term_key=groups[3].terms.last()
    )
    notary_agreed_pending = notary_public_factory.create(
        user_key=user_agreed_pending, term_key=groups[4].terms.last()
    )

    def status(terms_agreed=False, request_url="/"):
        """
        Returns mainly a request for the following terms_agreed cases:
            AnonymousUser: Not logged in user
            AgreedAndPending: User that agreed to one term but not to another
            False: Has not agreed to any of the existing terms
            True/Whatever: Has agreed to all terms
        """
        request = factory.get(request_url)
        if terms_agreed == "AnonymousUser":
            request.user = AnonymousUser()
            Setup = namedtuple("Setup", ["request", "response"])
            return Setup(request=request, response=Mock())
        elif terms_agreed == "AgreedAndPending":
            request.user = user_agreed_pending
            Setup = namedtuple("Setup", ["request", "response", "notary"])
            return Setup(request=request, response=Mock(), notary=notary_agreed_pending)
        elif not terms_agreed:
            request.user = user_not_agreed
            Setup = namedtuple("Setup", ["request", "response"])
            return Setup(request=request, response=Mock())
        else:
            request.user = user_agreed
            Setup = namedtuple("Setup", ["request", "response", "notary"])
            return Setup(request=request, response=Mock(), notary=notary_agreed)

    return status


@pytest.fixture
def users(user_factory):
    """
    Return either:
        * a superuser
        * a staff user with all available permissions for notarypublic and term
    """
    permissions = Permission.objects.filter(
        Q(codename__contains="notarypublic") | Q(codename__contains="term")
    )
    staff_user = user_factory.create(is_superuser=False, user_permissions=permissions)
    super_user = user_factory.create(is_superuser=True)

    def _send(user):
        user_choices = {
            "staff": staff_user,
            "sup_er": super_user,
        }
        return user_choices[user]

    return _send


@pytest.fixture
def many_terms(term_factory):
    return term_factory.create_batch(20)


@pytest.fixture
def many_terms_one_view_user(term_factory, user_factory, group):
    permissions = Permission.objects.filter(
        Q(Q(codename__contains="notarypublic") & Q(codename__contains="view"))
        | Q(Q(codename__contains="term") & Q(codename__contains="view"))
    )
    term_factory.create_batch(20)
    staff_view_user = user_factory.create(
        is_superuser=False, groups=(group,), user_permissions=permissions
    )
    term_factory.create(group_key=group)
    return staff_view_user


@pytest.fixture
def agreed_users(notary_public_factory, users):
    Users = namedtuple("Users", ["staff", "sup_er"])
    the_users = Users(staff=users("staff"), sup_er=users("sup_er"))
    for each in the_users:
        notary_public_factory.create(user_key=each)
        notary_public_factory.create(user_key=each)
        notary_public_factory.create(user_key=each)
        notary_public_factory.create(user_key=each)
        notary_public_factory.create(user_key=each)
    return the_users
