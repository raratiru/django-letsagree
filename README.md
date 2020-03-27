[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/raratiru/django-letsagree.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/raratiru/django-letsagree/context:python)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/61b3e157f170421ca3388f83567a873a)](https://www.codacy.com/app/raratiru/django-letsagree?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=raratiru/django-letsagree&amp;utm_campaign=Badge_Grade)
[![Build Status](https://travis-ci.com/raratiru/django-letsagree.svg?branch=master)](https://travis-ci.com/raratiru/django-letsagree)
[![Coverage Status](https://coveralls.io/repos/github/raratiru/django-letsagree/badge.svg?branch=travis)](https://coveralls.io/github/raratiru/django-letsagree?branch=travis)
[![Updates](https://pyup.io/repos/github/raratiru/django-letsagree/shield.svg)](https://pyup.io/repos/github/raratiru/django-letsagree/)
[![Known Vulnerabilities](https://snyk.io/test/github/raratiru/django-letsagree/badge.svg?targetFile=test_setup%2Frequirements.txt)](https://snyk.io/test/github/raratiru/django-letsagree?targetFile=test_setup%2Frequirements.txt)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

[![Python Versions](https://img.shields.io/badge/Python-3.5%20|%203.6%20|%203.7%20|%203.8-%236600cc)](https://docs.djangoproject.com/en/dev/faq/install/#what-python-version-can-i-use-with-django)
[![Django Versions](https://img.shields.io/badge/Django-2.2%20|%203.0-brown.svg)](https://www.djangoproject.com/download/)
[![Database Window Functions](https://img.shields.io/badge/Database-Window%20Functions-important.svg)](https://www.sql-workbench.eu/dbms_comparison.html)

Let's Agree
======

Features
--------

* Terms [versioning](#version) in "[`deque`](https://docs.python.org/3.7/library/collections.html#collections.deque)-style" with `maxlen=1`.
* Per-Group Term association, per-User Term acceptance for each Group a user belongs to.
* [Max 1 query](#queries), either per request or per day for each logged-in user.
* [Multi-language](#translation) ready.
* [Freedom](#permissions) for each user to withdraw consent at any time.


About
---

`django-letsagree`is the result of an effort to follow the spirit of [The EU General Data Protection Regulation (GDPR)](https://eugdpr.org/).

A logged in user can belong to one or more Groups.

If one or more Groups are associated with `django-letsagree`, all users that login as members of those Groups will be asked to provide their consent to the Terms related with each Group. This action, will be recorded in the database.

The Terms associated with a Group, can be updated with newer versions.

Such a decision will trigger again the mechanism which asks for the consent of each user before allowing any other operation on the site.

If the user does not provide consent, the following actions are only allowed:

* Logout.
* View and delete all instances of own consent provided.
* View all Terms


Prerequisites
-------

* Python 3.5, 3.6, 3.7, 3.8
* Django 2.2, 3.0
* [Django Admin Site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/) (enabled by default in Django)
* A database with [Window Functions support](https://www.sql-workbench.eu/dbms_comparison.html)
* [`django-translated-fields`](https://github.com/matthiask/django-translated-fields)

Installation
-------
1. `pip install django-letsagree`

2. project/settings.py
    ```python
    INSTALLED_APPS = [
        ...
        'letsagree.apps.LetsagreeConfig',
        ...
    ]

    MIDDLEWARE = [
        ...
        'letsagree.middleware.LetsAgreeMiddleware',  # Near the end of the list
        ...
    ]
    ```

3. `<project>` is the name of the project that hosts django-letsagree

    project/settings.py:
    ```python
    MIGRATION_MODULES = {
        'letsagree': '<project>.3p_migrations.letsagree',
    }
    ```

4. Make sure [LANGUAGES](https://docs.djangoproject.com/en/dev/ref/settings/#languages) are properly set as explained in the [Translation](#translation) section.
  The default implementation will create as **many fields** as the number of `LANGUAGES` Django has set by default.


5. project/urls.py:

    ```python
    urlpatterns = [
            ...
            path('path/to/letsagree/', include('letsagree.urls')),
            ...
    ]
    ```

6. Create the migrations:

    ```python
    ./manage.py makemigrations letsagree
    ./manage.py migrate
    ```


### Notes on installation

* `django-letsagree` itself does not come with any migrations. It is recommended
    that you add migrations for its models in your project and avoid using the
    word `migrations` as the name of the folder.

    The relevant Django setting is [`MIGRATION_MODULES`](https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules).
    In the above example, we store migrations inside `<project>/<project>/3p_migrations`.
    

Settings
--------

### Default Settings
```python
LETSAGREE_CACHE = False
LETSAGREE_CSS = {}
LETSAGREE_JS = ()
LETSAGREE_LOGOUT_APP_NAME = 'admin'
LETSAGREE_BROWSER_TITLE = ''
LETSAGREE_BORDER_HEADER = ''
```
<a name='queries'></a>
### Database queries


The middleware generates one database query per request in order to make sure that the user has agreed to all the terms related with the Group(s) he belongs to.

If `LETSAGREE_CACHE = True`, [Django's Cache Framework](https://docs.djangoproject.com/en/dev/topics/cache/) will be used and only one database query will be generated by the middleware, every 24 hours.

`LETSAGREE_CACHE` is not enabled by default, because it exposes the unique `id` for each user by creating a cache record with key `'letsagree-<user id>'`.

Tip: [django-hashid-field](https://github.com/nshafer/django-hashid-field), is a library that obscures unique `id`s, without compromising their uniqueness.

<a name='translation'></a>
### Translation


**Watch your `LANGUAGES`**!

#### Database

By default `lestagree` installs [`django-translated-fields`](https://github.com/matthiask/django-translated-fields) to cater for translating the `title`, `summary` and `content` fields of the `Term` model. This library will create separate fields for each entry in the [`LANGUAGES`](https://docs.djangoproject.com/en/dev/ref/settings/#languages) list.

The first entry of this list is considered as the "default language". The relevant database field is marked as `blank=False` and it serves as a fallback value. This value is returned if an entry for the requested language does not exist.

All other fields that are related with the rest of the languages in the `LANGUAGES` list are marked as `blank=True` and can stay empty.

Although the [`LANGUAGE_CODE`](https://docs.djangoproject.com/en/dev/ref/settings/#language-code) setting is not directly related with `letsagree` or `django-translated-fields` it is **strongly** recommended to match the first language in the `LANGUAGES` setting.

Example:
```python
LANGUAGES = (('fr', 'French'), ('en', 'English'))
LANGUAGE_CODE = 'fr'
```
The model `Term` will include the following fields:
```python
{
    'title_fr': {'blank': False},
    'title_en': {'blank': True},
    'summary_fr': {'blank': False},
    'summary_en': {'blank': True},
    'content_fr': {'blank': False},
    'content_en': {'blank': True},
}
```

#### Strings

All strings in `django-letsagree` are marked with one of the following ways which allow translation:
* `django.utils.translation.gettext_lazy('<string>')`
* `{% trans "<string>" %}`

### Custom Form Assets

`django-letsagree` uses`letsagree/pending.html` template which extends `admin/index.html`. Through a `FormView` this template receives a `Formset` which includes all the `Terms` that should receive consent from the user.

`LETSAGREE_CSS` and `LETSAGREE_JS` when set, pass the relevant assets in the `Media` class of the `Form` that serves as the basis of the above mentioned Formset. The syntax is described in the relevant [django documentation.](https://docs.djangoproject.com/en/dev/topics/forms/media/#assets-as-a-static-definition)

A good starting point could be the default css file provided by `django-letsagree`:

settings.py:
```python
LETSAGREE_CSS = {'all': ('letsagree/letsagree.css',)}
```

Of course, one can completely [override the templates](https://docs.djangoproject.com/en/dev/howto/overriding-templates/).

In that case, bear in mind that if `{{ empty_form }}` is False, `{{ form }}` contains a formset.


### Other settings

* `LETSAGREE_LOGOUT_APP_NAME`: A logout link will appear on the top right corner of both templates.

  This is formed as `reverse(<LETSAGREE_LOGOUT_APP_NAME>:logout)`.

  The logout link defaults to `reverse('admin:logout')`.

* `LETSAGREE_BROWSER_TITLE`: A title for the default template.
* `LETSAGREE_BORDER_HEADER`: Text that will appear on the top left corner of the default template.

<a name='permissions'></a>
Permissions
-----------

It is your responsibility to assign every new user to a Group associated with `django-letsagree`. This group should at least include the `delete_notarypublic` permission in case a user whishes to revoke his consent.

If all permissions for `django-letsagree` models are delegated to a group, the below table illustrates what actions are allowed for user, with either `is_staff == True` or `is_superuser == True`:


| Actions | superuser own entries | superuser other entries | admin-user own entries | admin-user other entries |
| :-----| :------------------:| :--------------------: | :-------------------:  | :---------------------: |
| view_term | **True** | **True** | **True** |**True**|
| add_term | **True** |  | **True** |  |
| change_term | False | False | False | False |
| delete_term | False | False | False | False |
| view_notarypublic | **True** | **True** |**True** | False |
| add_notarypublic | False |  | False |  |
| change_notarypublic | False | False | False | False |
| delete_notarypublic | **True** | False | **True** | False |

### Term changelist contents

Users who have permission to add a new term, are allowed to read all the available terms. Otherwise, each user can only read the terms related to the group that he or she belongs to.

<a name='version'></a>
New Term Version
----------------
If two instances of Term associate with the same Group, the instance saved-last is the latest version. All logged in users have to provide consent for this latest version, independently of any previous consent they may have or have not given for the Terms associated with this Group.

`django-letsagree` takes into account if a logged-in user has provided consent only for the latest version of each Term associated with the Groups he belongs to. If not, the user can only logout or visit `django-letsagree` admin page retaining the right to delete any instances of consent he has provided.

Tests
-----

To run the test suite, you need:

* Virtualenv with tox installed.
* PostgreSQL, MariaDB/MySQL databases with the same user, password, database name.
* The following environment variables set: `TOX_DB_NAME`, `TOX_DB_USER`, `TOX_DB_PASSWD`.

Unfortunatelly, the test suite is rather complicated. Sorry!

### Coverage: Not tested

* [`LETSAGREE_CSS`](https://github.com/raratiru/django-letsagree/blob/9436ddabb4467477ecb39d94fd09b6f574e9384f/letsagree/forms.py#L42-L44)
* [`LETSAGREE_JS`](https://github.com/raratiru/django-letsagree/blob/9436ddabb4467477ecb39d94fd09b6f574e9384f/letsagree/forms.py#L42-L44)
* [`letsagree.admin.term_parents`](https://github.com/raratiru/django-letsagree/blob/9436ddabb4467477ecb39d94fd09b6f574e9384f/letsagree/admin.py#L23-L27)

Changelog
---------
1.0.3: Only users with add_perm can see all the Terms in changelist

1.0.2: Addressed codacy reports, updated readme, installed pyup, snyk

1.0.1: Added Travis, Coverage, LGTM, PyUp CI
