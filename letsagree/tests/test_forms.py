#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/tests/test_forms.py
#
#       Creation Date : Sat 23 Mar 2019 07:29:49 PM EET (19:29)
#
#       Last Modified : Mon 08 Apr 2019 03:18:30 PM EEST (15:18)
#
# ==============================================================================

from letsagree import forms


def test_pending_form():
    form = forms.PendingConsentForm()
    # Test that save is not responding
    result = form.save(
        ("blah", "tt"), {"does nothing": 3, None: "3"}, random_variable="4"
    )
    assert result is None
    # All fields are disabled except agree
    popped = form.fields.pop("agree")
    assert popped.disabled is False

    for each in form.fields.values():
        assert each.disabled is True
