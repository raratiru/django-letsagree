#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from letsagree import models


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
        """
        The fields here are not fine-grained based on the active language because
        get_language() has contenxt only within the request/response cycle.
        In this case, it happens within the View insance where modelformset_factory
        is initialized with the appropriate fields.

        If needed, the default language should be explicitly queried from the
        settings.DEFAULT_LANGUAGE.

        In this case, however, the modelform is not enabled in the admin.
        """

        model = models.Term
        fields = "__all__"
