#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : test_setup/settings.py
#
#       Creation Date : Tue 09 Apr 2019 01:19:13 AM EEST (01:19)
#
#       Last Modified : Tue 09 Apr 2019 03:31:42 AM EEST (03:31)
#
# ==============================================================================

import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = 'fsfie4j234*^%Dkkvkdnf8(*^@#()Fjvhdfi3))^%$'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'letsagree',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'letsagree.middleware.LetsAgreeMiddleware',
]

LANGUAGES = (('fr', 'French'), ('en', 'English'))
LANGUAGE_CODE = 'fr'

ROOT_URLCONF = 'test_setup.urls'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

MIGRATION_MODULES = {
    'letsagree': 'test_setup.3p_migrations.letsagree',
}
