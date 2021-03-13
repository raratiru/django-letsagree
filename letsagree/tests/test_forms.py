#!/usr/bin/env python
# -*- coding: utf-8 -*-

from letsagree import forms


def test_pending_form():
    form = forms.PendingConsentForm()
    # Test that save is not responding
    result = form.save(commit=True)
    assert result is None
    # All fields are disabled except agree
    popped = form.fields.pop("agree")
    assert popped.disabled is False

    for each in form.fields.values():
        assert each.disabled is True
