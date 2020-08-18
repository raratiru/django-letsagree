#!/usr/bin/env python
# -*- coding: utf-8 -*-


# ==============================================================================
#
#       File Name : letsagree/views.py
#
#       Creation Date : Sun 27 Jan 2019 07:54:42 PM EET (19:54)
#
#       Last Modified : Tue 18 Aug 2020 11:15:32 AM EEST (11:15)
#
# ==============================================================================

from django.db import transaction
from django.conf import settings
from django.core.cache import cache
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from django.views.generic import FormView
from letsagree import models
from letsagree.forms import PendingAgreementFormSet
from letsagree.helpers import get_logout_url


class PendingView(FormView):
    http_method_names = ["get", "post"]
    template_name = "letsagree/pending.html"
    form_class = PendingAgreementFormSet

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Http404()
        self.success_url = request.GET.get("next")
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        """
        Pass to the modelformset_factory a queryset argument to create the
        formset that represents the terms needing the user's consent.
        """
        kwargs = super().get_form_kwargs()
        # Avoid KeyError that randomly occurs
        user_id = self.request.user.id
        kwargs["queryset"] = models.Term.objects.get_pending_terms(user_id)
        return kwargs

    def form_valid(self, form):
        """
        The user has agreed to the terms, save each agreement in the database.

        bulk_create could be used, but it is only compatible with PostgreSQL
        which, at the moment, is the only db able to handle autoincremented pk.
        """
        user_id = self.request.user.id
        for sub_form in form:
            with transaction.atomic():
                models.NotaryPublic.objects.create(
                    term_key_id=sub_form.instance.id, user_key_id=user_id
                )
        cache_key = "letsagree-{0}".format(user_id)
        cache.set(cache_key, False, 24 * 3600)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["browser_title"] = getattr(
            settings, "LETSAGREE_BROWSER_TITLE", _("Let's Agree")
        )
        context["border_header"] = getattr(settings, "LETSAGREE_BORDER_HEADER", "")
        context["user"] = self.request.user
        context["logout_url"] = get_logout_url()

        if len(context["form"]) == 0:
            context["empty_form"] = True
        else:
            context["empty_form"] = False

        return context
