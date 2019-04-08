#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/tests/test_models.py
#
#       Creation Date : Sat 23 Mar 2019 12:01:41 AM EET (00:01)
#
#       Last Modified : Mon 01 Apr 2019 08:55:13 PM EEST (20:55)
#
# ==============================================================================

import pytest

from letsagree import models


pytestmark = pytest.mark.django_db


def test_strings(queries, django_assert_num_queries):
    queries(terms_agreed=True)
    with django_assert_num_queries(1):
        term = models.Term.objects.first()
        string = term.__str__()

    group_name = term.group_key.name
    assert str(group_name) in string
    assert str(term.id) in string
    assert str(term.date_created.strftime("%Y-%m-%d-%T")) in string

    with django_assert_num_queries(1):
        notary_public = models.NotaryPublic.objects.first()
        string = notary_public.__str__()

    assert str(notary_public.id) in string
    assert str(notary_public.term_key_id) in string
