#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/forms.py
#
#       Creation Date : Mon 25 Feb 2019 05:44:28 PM EET (17:44)
#
#       Last Modified : Mon 08 Apr 2019 03:16:38 PM EEST (15:16)
#
# ==============================================================================

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from letsagree import models
from translated_fields import to_attribute


class PendingConsentForm(forms.ModelForm):
    agree = forms.BooleanField(required=True, label=_("I Give my Consent"))

    def save(self, commit=False):
        """
        There is nothing to save. This form is a building block of a formset
        with read-only contents.
        """
        pass

    def __init__(self, *args, **kwargs):
        """
        All Fields are disabled. They are rendered as read-only fields.
        """
        super().__init__(*args, **kwargs)
        for field in self.fields.keys():
            if field == "agree":
                continue
            self.fields[field].disabled = True

    class Media:
        css = getattr(settings, "LETSAGREE_CSS", dict())
        js = getattr(settings, "LETSAGREE_JS", tuple())

    class Meta:
        model = models.Term
        fields = (
            "date_created",
            to_attribute("summary"),
            to_attribute("content"),
            "agree",
        )


PendingAgreementFormSet = forms.modelformset_factory(
    models.Term, form=PendingConsentForm, extra=0
)
