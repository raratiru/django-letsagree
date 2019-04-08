#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/models.py
#
#       Creation Date : Sun 27 Jan 2019 07:54:42 PM EET (19:54)
#
#       Last Modified : Mon 01 Apr 2019 06:02:32 PM EEST (18:02)
#
# ==============================================================================

from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from letsagree.querysets import TermQS
from translated_fields import TranslatedFieldWithFallback


class BaseRelatedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related()


class Term(models.Model):
    group_key = models.ForeignKey(
        Group,
        on_delete=models.PROTECT,
        related_name="terms",
        verbose_name=_("Related Group"),
    )
    title = TranslatedFieldWithFallback(
        models.CharField(max_length=63, verbose_name=_("Title"), db_index=True)
    )
    summary = TranslatedFieldWithFallback(models.TextField(verbose_name=_("Summary")))
    content = TranslatedFieldWithFallback(
        models.TextField(verbose_name=_("Terms and Conditions"))
    )

    date_created = models.DateTimeField(
        verbose_name=_("Date and Time of Document Creation"),
        default=timezone.now,
        db_index=True,
    )

    objects = BaseRelatedManager.from_queryset(TermQS)()

    def __str__(self):
        return '{0}, Group:"{1}" on {2}, {3}'.format(
            self.id,
            self.group_key.name,
            self.date_created.strftime("%Y-%m-%d-%T"),
            self.title,
        )

    class Meta:
        verbose_name = _("Terms & Conditions")
        verbose_name_plural = _("Terms & Conditions")


class NotaryPublic(models.Model):
    user_key = models.ForeignKey(
        get_user_model(),
        verbose_name=_("User"),
        on_delete=models.PROTECT,
        related_name="agreed_terms",
    )
    term_key = models.ForeignKey(
        Term,
        verbose_name=_("Terms and Conditions"),
        on_delete=models.PROTECT,
        related_name="users_agreed",
    )
    date_signed = models.DateTimeField(
        verbose_name=_("Date and Time of User Consent"),
        default=timezone.now,
        db_index=True,
    )

    objects = BaseRelatedManager()

    def __str__(self):
        return "{0}: User:{1}, Term-id:{2}".format(
            self.id, self.user_key.username, self.term_key_id
        )

    class Meta:
        verbose_name = _("Notary Public")
        verbose_name_plural = _("Notary Public")
        unique_together = ("user_key", "term_key")
