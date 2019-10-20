#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/tests/test_admin.py
#
#       Creation Date : Mon 01 Apr 2019 09:09:39 PM EEST (21:09)
#
#       Last Modified : Sun 20 Oct 2019 03:12:32 PM EEST (15:12)
#
# ==============================================================================

import pytest

from django.contrib.admin.sites import AdminSite
from django.core.exceptions import PermissionDenied
from django.test.client import Client
from django.urls import reverse
from letsagree import admin, models


pytestmark = pytest.mark.django_db

site = AdminSite()


@pytest.mark.parametrize(
    "user,action",
    [
        ("staff", "delete"),
        ("staff", "change"),
        ("staff", "add"),
        ("sup_er", "delete"),
        ("sup_er", "change"),
        ("sup_er", "add"),
    ],
)
def test_term_actions(users, user, action, term, rf):
    model_admin = admin.TermAdmin(models.Term, site)

    if action == "add":
        url = reverse("admin:letsagree_term_{0}".format(action))
    else:
        url = reverse("admin:letsagree_term_{0}".format(action), args=(term.id,))

    request = rf.get(url)
    request.user = users(user)

    view_obj = getattr(model_admin, "{0}_view".format(action))

    # No one can delete
    if action == "delete":
        with pytest.raises(PermissionDenied):
            view_obj(request, object_id=str(term.id))

    # Every admin user with permissions can view but cannot change
    elif action == "change":
        view = view_obj(request, object_id=str(term.id))
        assert view.status_code == 200
        assert "delete" not in view.rendered_content
        assert "readonly" in view.rendered_content
        assert '<input type="submit"' not in view.rendered_content

    # Every admin user with permissions can add
    elif action == "add":
        view = view_obj(request)
        assert view.status_code == 200


def test_term_changelist(users, many_terms, rf, django_assert_num_queries):
    model_admin = admin.TermAdmin(models.Term, site)

    url = reverse("admin:letsagree_term_changelist")

    request = rf.get(url)
    request.user = users("staff")
    with django_assert_num_queries(3):
        qs = model_admin.get_queryset(request)
        assert qs.count() == len(many_terms)
    with django_assert_num_queries(3):
        view = model_admin.changelist_view(request)
        assert view.status_code == 200


def test_view_user_term_changelist(many_terms_one_view_user, rf):
    model_admin = admin.TermAdmin(models.Term, site)

    url = reverse("admin:letsagree_term_changelist")

    request = rf.get(url)
    request.user = many_terms_one_view_user
    qs = model_admin.get_queryset(request)
    assert models.Term.objects.count() > 1
    assert qs.count() == 1


@pytest.mark.parametrize(
    "main_user,other_user,action",
    [
        ("staff", "sup_er", "delete"),
        ("staff", "sup_er", "change"),
        ("staff", "sup_er", "add"),
        ("sup_er", "staff", "delete"),
        ("sup_er", "staff", "change"),
        ("sup_er", "staff", "add"),
    ],
)
def test_notarypublic_actions(main_user, other_user, action, agreed_users, rf):
    model_admin = admin.NotaryPublicAdmin(models.NotaryPublic, site)
    active_user = getattr(agreed_users, main_user)
    inactive_user = getattr(agreed_users, other_user)
    agreement_id = active_user.agreed_terms.last().id

    if action == "add":
        url = reverse("admin:letsagree_notarypublic_{0}".format(action))
    else:
        url = reverse(
            "admin:letsagree_notarypublic_{0}".format(action), args=(agreement_id,)
        )

    request = rf.get(url)

    # A user can only delete his agreements
    if action == "delete":
        request.user = active_user
        view = model_admin.delete_view(request, object_id=str(agreement_id))
        assert view.status_code == 200
        data = {"post": "yes", "_popup": "1"}
        client = Client()
        client.force_login(request.user)
        post_view = client.post(url, data)
        assert post_view.status_code == 302
        assert post_view.url == reverse("admin:letsagree_notarypublic_changelist")
        # Another (super)user cannot delete the active user's agreement
        request.user = inactive_user
        with pytest.raises(PermissionDenied):
            model_admin.delete_view(request, object_id=str(agreement_id))

    elif action == "add":
        # Noone is allowed to add any agreement.
        request.user = active_user
        with pytest.raises(PermissionDenied):
            model_admin.add_view(request)

    elif action == "change":
        # The active user can view the agreement (in order to delete it)
        request.user = active_user
        view = model_admin.change_view(request, object_id=str(agreement_id))

        assert view.status_code == 200
        assert "delete" in view.rendered_content
        assert "readonly" in view.rendered_content
        assert '<input type="submit"' not in view.rendered_content

        if inactive_user.is_superuser:
            # The inactive super user can view the active user's agreement
            # get_queryset() guarantees that the inactive admin user will not
            # have access to the change view of another user's agreement.
            # It is tested next.
            view = model_admin.change_view(request, object_id=str(agreement_id))
            assert view.status_code == 200


@pytest.mark.parametrize("user,", ["staff", "sup_er"])
def test_notarypublic_changelist(
    agreed_users, user, rf, django_assert_num_queries, django_assert_max_num_queries
):
    model_admin = admin.NotaryPublicAdmin(models.NotaryPublic, site)
    user = getattr(agreed_users, user)

    url = reverse("admin:letsagree_notarypublic_changelist")

    request = rf.get(url)
    request.user = user
    # A regular admin user can only see his agreements
    if not user.is_superuser:
        with django_assert_num_queries(2):
            qs = model_admin.get_queryset(request)
            assert qs.count() == user.agreed_terms.count()
    # A superuser can see all agreements
    else:
        with django_assert_num_queries(2):
            qs = model_admin.get_queryset(request)
            assert qs.count() == models.NotaryPublic.objects.all().count()

    # Superuser 3 queries, staff 5 queries due to permissions queries
    with django_assert_max_num_queries(5):
        view = model_admin.changelist_view(request)
        assert view.status_code == 200
