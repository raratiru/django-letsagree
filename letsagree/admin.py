#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/admin.py
#
#       Creation Date : Sun 27 Jan 2019 07:54:42 PM EET (19:54)
#
#       Last Modified : Sun 20 Oct 2019 02:31:39 PM EEST (14:31)
#
# ==============================================================================

from django.conf import settings
from django.contrib import admin
from letsagree import models
from translated_fields import TranslatedFieldAdmin, to_attribute
from django.http import HttpResponseRedirect
from django.urls import reverse


term_parents = (
    (admin.ModelAdmin,)
    if len(settings.LANGUAGES) < 2
    else (TranslatedFieldAdmin, admin.ModelAdmin)
)


@admin.register(models.Term)
class TermAdmin(*term_parents):
    autocomplete_fields = ("group_key",)
    list_display = ("id", "group_key", "date_created", "title")
    list_display_links = ("id", "date_created", "title")
    readonly_fields = ("date_created",)
    search_fields = ("id", to_attribute("title"))

    @staticmethod
    def has_delete_permission(request, obj=None):
        return False

    @staticmethod
    def has_change_permission(request, obj=None):
        return False

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.has_perm("letsagree.add_term"):
            return qs
        else:
            return qs.filter(group_key__user=request.user)


@admin.register(models.NotaryPublic)
class NotaryPublicAdmin(admin.ModelAdmin):
    autocomplete_fields = ("term_key", "user_key")
    list_display = ("id", "date_signed", "user_key", "term_key")
    list_display_links = ("id", "date_signed", "term_key")
    readonly_fields = ("date_signed",)
    search_fields = ("id", "user_key__username")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user_key_id=request.user.id)

    @staticmethod
    def has_add_permission(request):
        return False

    @staticmethod
    def has_delete_permission(request, obj=None):
        if obj:
            return request.user.id == obj.user_key_id
        return False

    @staticmethod
    def has_change_permission(request, obj=None):
        return False

    def response_delete(self, request, obj_display, obj_id):
        return HttpResponseRedirect(reverse("admin:letsagree_notarypublic_changelist"))
