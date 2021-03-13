#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.urls import path
from letsagree import views

app_name = "letsagree"

urlpatterns = [path("", views.PendingView.as_view(), name="pending")]
