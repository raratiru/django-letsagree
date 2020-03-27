#!/usr/bin/env python


# ==============================================================================
#
#       File Name : letsagree/middleware.py
#
#       Creation Date : Mon 28 Jan 2019 01:20:20 PM EET (13:20)
#
#       Last Modified : Fri 27 Mar 2020 08:50:03 PM EET (20:50)
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
        redirect_url = ConsentEvaluator(request).get_redirect_url()
        if redirect_url:
            return redirect(redirect_url)
        else:
            return self.get_response(request)


class ConsentEvaluator:
    def __init__(self, request):
        self.user_id = request.user.id
        self.path = request.path
        self.request_needs_investigation = self.validate_user_intention()
        self.get_next = request.GET.get("next") or request.path

    def validate_user_intention(self):
        """
        Check if a logged user exists and whether this user is requesting a url
        that requires previous consent of the relevant tos.
        excluded urls form consent are:
            * The letsagree form consent url
            * The logout url
            * All letsagree admin urls, except for the request to add a new tos.
              (the user who is entitled to add a new tos, has only the right to
              do so if he has already agreed to the current term in effect.)
            *
        """
        logout_url_app = (
            getattr(settings, "LETSAGREE_LOGOUT_APP_NAME", "admin") or "admin"
        )
        logout_url = (
            reverse("{0}:logout".format(logout_url_app)) if logout_url_app else ""
        )
        satisfied_prerequisites = all(
            (
                self.user_id,
                self.path != reverse("letsagree:pending"),
                self.path != logout_url,
                any(
                    (
                        not self.path.startswith(
                            reverse("admin:app_list", args=("letsagree",))
                        ),
                        "add" in self.path,
                    )
                ),
            )
        )
        return satisfied_prerequisites

    def get_or_set_cache(self, cache_key):
        """
        if cache exists:
            return its value
        else:
            set cache and return its new value
        """
        user_consent_required = cache.get(cache_key, None)

        if user_consent_required is None:
            cache_value = Term.objects.get_pending_terms(self.user_id).exists()
            cache.set(cache_key, cache_value, 24 * 3600)
            return cache_value
        else:
            return user_consent_required

    def consent_is_required(self):
        """
        Return True if consent is required, else False.
        If cache is enabled:
            * check or set the cache
        else;
            * query for the status

        By default cache is deactivated because it exposes the user id which
        uniquely identifies a user in the database. Nonetheless,
        django-hashid-field (https://github.com/nshafer/django-hashid-field),
        can obscure the user id while keeping its uniqueness.
        """
        if getattr(settings, "LETSAGREE_CACHE", False):
            cache_key = "letsagree-{0}".format(self.user_id)
            return self.get_or_set_cache(cache_key)

        else:
            return Term.objects.get_pending_terms(self.user_id).exists()

    def get_next_parameter(self):
        """
            If next parameter exists in request, set it also in the redirect
            unless it equals the url of the consent form.
        """
        return (
            "?next={0}".format(self.get_next)
            if self.get_next and self.get_next != reverse("letsagree:pending")
            else None
        )

    def get_redirect_url(self):
        """
        If user has already agreed:
            * Return None
        else:
            * Return Redirect URL
        """
        result = None
        if self.request_needs_investigation:
            if self.consent_is_required():
                redirect_url = reverse("letsagree:pending")
                next_url = self.get_next_parameter()
                result = "{0}{1}".format(redirect_url, next_url)
        return result
