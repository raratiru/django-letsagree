#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/urls.py
#
#       Creation Date : Wed 06 Feb 2019 07:49:20 PM EET (19:49)
#
#       Last Modified : Mon 08 Apr 2019 03:03:37 PM EEST (15:03)
#
# ==============================================================================

from django.urls import path
from letsagree import views

app_name = "letsagree"

urlpatterns = [path("", views.PendingView.as_view(), name="pending")]
