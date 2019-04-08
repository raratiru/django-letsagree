#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : test_setup/settings.py
#
#       Creation Date : Tue 09 Apr 2019 01:19:13 AM EEST (01:19)
#
#       Last Modified : Wed 10 Apr 2019 08:18:40 PM EEST (20:18)
#
# ==============================================================================

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    "default": {
        "ENGINE": os.environ["TOX_DB_ENGINE"],
        "NAME": os.environ["TOX_DB_NAME"],
        "USER": os.environ["TOX_DB_USER"],
        "PASSWORD": os.environ["TOX_DB_PASSWD"],
    }
}

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "letsagree",
]


LANGUAGE_CODE = "en"

LANGUAGES = (("en", "English"),)

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "letsagree.middleware.LetsAgreeMiddleware",
]

ROOT_URLCONF = "test_setup.urls"

SECRET_KEY = "fsfie4j234*^%Dkkvkdnf8(*^@#()Fjvhdfi3))^%$"

STATIC_URL = "/static/"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ]
        },
    }
]

USE_I18N = False

USE_L10N = False
