#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : test_setup.urls.py
#
#       Creation Date : Tue 09 Apr 2019 03:25:45 AM EEST (03:25)
#
#       Last Modified : Tue 09 Apr 2019 03:27:15 AM EEST (03:27)
#
# ==============================================================================


from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("letsagree/", include("letsagree.urls")),
]
