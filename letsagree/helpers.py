#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django.conf import settings
from django.urls import reverse, NoReverseMatch


def get_named_url():
    app_name = getattr(settings, "LETSAGREE_LOGOUT_APP_NAME", False)
    logout_named_url = getattr(settings, "LETSAGREE_LOGOUT_URL", "admin:logout")

    if app_name:
        return "{0}:logout".format(app_name)
    else:
        return logout_named_url


def get_logout_url():
    try:
        return reverse(get_named_url())
    except NoReverseMatch:
        return ""
