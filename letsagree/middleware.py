#!/usr/bin/env python


# ==============================================================================
#
#       File Name : letsagree/middleware.py
#
#       Creation Date : Mon 28 Jan 2019 01:20:20 PM EET (13:20)
#
#       Last Modified : Mon 08 Apr 2019 03:46:40 PM EEST (15:46)
#
# ==============================================================================

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from django.urls import reverse
from letsagree.models import Term


class LetsAgreeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """
        For a logged in user:
            During each request, check if the user has agreed to the terms
            and conditions. If not, redirect to a form where he can provide
            consent in order to continue.

            By default cache is deactivated because it exposes the user id which
            uniquely identifies a user in the database. Nonetheless,
            django-hashid-field (https://github.com/nshafer/django-hashid-field),
            can obscure the user id while keeping its uniqueness.
        """
        # Avoid KeyError that randomly occurred in views.PendingView
        user_id = request.session.get("_auth_user_id", request.user.id)
        qs = Term.objects.get_pending_terms(user_id)
        logout_url_app = (
            getattr(settings, "LETSAGREE_LOGOUT_APP_NAME", "admin") or "admin"
        )
        logout_url = (
            reverse("{0}:logout".format(logout_url_app)) if logout_url_app else ""
        )
        if all(
            (
                user_id,
                request.path != reverse("letsagree:pending"),
                request.path != logout_url,
                any(
                    (
                        not request.path.startswith(
                            reverse("admin:app_list", args=("letsagree",))
                        ),
                        "add" in request.path,
                    )
                ),
            )
        ):
            if getattr(settings, "LETSAGREE_CACHE", False):
                cache_key = "letsagree-{0}".format(user_id)
                user_consent_required = cache.get(cache_key)
                if user_consent_required is None:
                    cache.set(cache_key, qs.exists(), 24 * 3600)
                    user_consent_required = cache.get(cache_key)
            else:
                user_consent_required = qs.exists()
            if user_consent_required:
                url = reverse("letsagree:pending")
                get_next = request.GET.get("next") or request.path
                if all((get_next, get_next != reverse("letsagree:pending"))):
                    next_url = "?next={0}".format(get_next)
                else:
                    next_url = None
                return redirect("{0}{1}".format(url, next_url))
        return self.get_response(request)
