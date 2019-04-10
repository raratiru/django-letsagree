#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/querysets.py
#
#       Creation Date : Tue 29 Jan 2019 10:51:29 AM EET (10:51)
#
#       Last Modified : Fri 22 Mar 2019 11:48:45 PM EET (23:48)
#
# ==============================================================================

from django.db import models
from django.db.models import F, Window
from django.db.models.functions import FirstValue


class TermQS(models.QuerySet):
    def prepare_active_terms(self, user_id):
        """
        The query opens a window, groups all entries by the group they belong to,
        orders them by the date and annotates the first one of each group
        to a field called 'active_terms'.
        """
        return (
            self.filter(group_key__user=user_id)
            .annotate(
                active_terms=Window(
                    expression=FirstValue("id"),
                    partition_by=["group_key"],
                    order_by=F("date_created").desc(),
                )
            )
            .distinct()
        )

    def get_pending_terms(self, user_id):
        """
        Query that returns the user's pending to be signed terms.

        1 db hit.

        values_list('active_terms') returns only the latest active term
        which is currently in effect for each group.

        Consequently, it is possible for a user to miss -and never agree with-
        a term that was in effect in a period during which he did not
        happen to log in. He will agree, however, to the newest term that
        follows the missed one.
        """
        return self.filter(
            id__in=self.prepare_active_terms(user_id).values_list("active_terms")
        ).exclude(users_agreed__user_key_id=user_id)

    def get_signed_agreements(self, user_id):
        """
        Query that returns the user's signed agreements.

        2 db hits

        This query prefetches, for each term, the agreement made by the user,
        in order to allow access without hitting the database when
        the date of the signature has to be retrieved. One agreement per
        term is expected, hoewever and order_by is provided in case more
        agreements exist.

        values_list('active_terms') returns only the latest term
        which is currently in effect for each group.
        """
        from letsagree.models import NotaryPublic

        return (
            self.filter(
                id__in=self.prepare_active_terms(user_id).values_list("active_terms")
            )
            .filter(users_agreed__user_key_id=user_id)
            .prefetch_related(
                models.Prefetch(
                    "users_agreed",
                    queryset=(
                        NotaryPublic.objects.filter(user_key_id=user_id).order_by(
                            "-date_signed"
                        )
                    ),
                    to_attr="signature_dates",
                )
            )
        )
