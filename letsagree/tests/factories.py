#!/usr/bin/env python
# -*- coding: utf-8 -*-
import factory

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from letsagree import models


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Faker("user_name")
    password = factory.Faker("password")
    email = factory.Faker("email")
    is_active = True
    is_staff = True
    is_superuser = factory.Iterator([False, True], cycle=True)

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for group in extracted:
                self.groups.add(group)

    @factory.post_generation
    def user_permissions(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            # A list of groups were passed in, use them
            for permission in extracted:
                self.user_permissions.add(permission)


Meta = type("Meta", (), {"model": models.Term})
main = {
    "__module__": "letsagree.tests.factories",
    "group_key": factory.SubFactory("letsagree.tests.factories.GroupFactory"),
    "Meta": Meta,
}
summaries = {
    "summary_{0}".format(lang[0]): factory.Faker("paragraphs", nb=3)
    for lang in settings.LANGUAGES
}
contents = {
    "content_{0}".format(lang[0]): factory.Faker("paragraphs", nb=12)
    for lang in settings.LANGUAGES
}
attrs = {**main, **summaries, **contents}

TermFactory = type("TermFactory", (factory.django.DjangoModelFactory,), attrs)


class GroupFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.Sequence(lambda n: "Group {0}".format(n))
    # terms = factory.RelatedFactory(TermFactory, 'group_key')


class NotaryPublicFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.NotaryPublic

    user_key = factory.SubFactory(UserFactory)
    term_key = factory.SubFactory(TermFactory)
