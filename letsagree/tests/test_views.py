#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/tests/test_viws.py
#
#       Creation Date : Sat 23 Mar 2019 08:42:45 PM EET (20:42)
#
#       Last Modified : Tue 18 Aug 2020 11:26:18 AM EEST (11:26)
#
# ==============================================================================

import pytest
import re
import sqlite3

from django.conf import settings
from django.test import RequestFactory
from django.urls import reverse
from letsagree import views, models, forms

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
@pytest.mark.parametrize(
    "terms_agreed,request_url,agree_queries", [(True, "/", 2), (False, "/", 1)]
)
def test_view_structure(
    queries,
    django_assert_num_queries,
    settings,
    terms_agreed,
    request_url,
    agree_queries,
):
    setup = queries(terms_agreed, request_url)
    settings.LETSAGREE_BORDER_HEADER = "THE HEADER"
    settings.LETSAGREE_BROWSER_TITLE = "My Title"

    # Set once the logout url to test if it is rendered
    if terms_agreed:
        settings.LETSAGREE_LOGOUT_APP_NAME = None  # By default is 'admin'
    else:
        settings.LETSAGREE_LOGOUT_APP_NAME = "foo"
    # Test Pending View
    with django_assert_num_queries(1):
        the_view = views.PendingView.as_view()
        response = the_view(setup.request)
    assert response.status_code == 200
    assert re.search(r"title>[\r\n]?My Title", response.rendered_content)
    assert "THE HEADER" in response.rendered_content

    if terms_agreed:
        assert "There are no pending agreements" in response.rendered_content
        assert reverse("admin:logout") in response.rendered_content
    elif terms_agreed is None:
        assert "There are no pending agreements" not in response.rendered_content
        assert reverse("admin:logout") in response.rendered_content
    else:
        assert "There are no pending agreements" not in response.rendered_content
        assert "LOG OUT" not in response.rendered_content


# @pytest.mark.parametrize(
#     "the_string,the_result",
#     [
#         ("admin", "admin:logout"),
#         ("admin:", "admin:logout"),
#         ("admin:logout_view", "admin:logout_view"),
#         ("", None),
#         (False, None),
#     ],
# )
# def test_named_url(the_string, the_result):
#     view = views.PendingView()
#     assert view.get_logout_string(the_string) == the_result


@pytest.mark.skipif(
    all(
        (
            float(".".join(sqlite3.sqlite_version.split(".")[:2])) < 3.25,
            "sqlite3" in settings.DATABASES["default"]["ENGINE"],
        )
    ),
    reason="Window Function is not supported in this SQLite version",
)
def test_404_redirect(client, admin_client):
    response = client.get("/letsagree/")
    assert response.status_code == 404
    response = admin_client.get("/letsagree/")
    assert response.status_code == 200


@pytest.mark.skipif(
    all(
        (
            float(".".join(sqlite3.sqlite_version.split(".")[:2])) < 3.25,
            "sqlite3" in settings.DATABASES["default"]["ENGINE"],
        )
    ),
    reason="Window Function is not supported in this SQLite version",
)
def test_view_post(queries, admin_client, settings):
    setup = queries(False)
    qs = models.Term.objects.get_pending_terms(setup.request.user.id)
    initial_data = qs.values()
    term_ids = qs.values_list("id")
    assert len(term_ids) == 3
    data = {
        "form-TOTAL_FORMS": "3",
        "form-INITIAL_FORMS": "3",
        "form-MAX_NUM_FORMS": "",
        "form-0-agree": True,
        "form-1-agree": True,
        "form-2-agree": True,
    }
    # Provide the data for a valid formset
    for count, item in enumerate(initial_data):
        for key, value in item.items():
            key_name = "form-{0}-{1}".format(count, key)
            data[key_name] = value

    # Test formset is valid and formset does not save to db
    formset = forms.PendingAgreementFormSet(data=data)
    assert formset.is_valid()
    assert formset.save() == [None, None, None]

    # Create the post request
    factory = RequestFactory()
    request = factory.post("{0}?next=/".format(reverse("letsagree:pending")), data)
    request.user = setup.request.user
    # User has not agreed to any terms yet
    assert request.user.agreed_terms.count() == 0
    the_view = views.PendingView.as_view()
    response = the_view(request)
    assert response.status_code == 302
    # Success url is the next url provided
    # Edge case: Next url not set during post, will raise 500 error. Is it
    # possible?
    assert response.url == "/"
    assert request.user.agreed_terms.count() == 3
    assert set(request.user.agreed_terms.values_list("term_key_id")) == set(term_ids)
