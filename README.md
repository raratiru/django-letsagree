Let's Agree
======

**This project is not yet published to pypi. It can be installed from github.**

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
* View all terms


Prerequisites
-------

* Python 3.5, 3.6, 3.7
* Django 2.1, 2.2
* [Django Admin Site](https://docs.djangoproject.com/en/dev/ref/contrib/admin/)
* A database with [Window Functions support](https://www.sql-workbench.eu/dbms_comparison.html)

Installation
-------
* `pip install django-letsagree`

* project/settings.py
    ```python
    INSTALLED_APPS = [
        ...,
        'letsagree',
        ...,
    ]

    MIDDLEWARE = [
        ...
        'letsagree.middleware.LetsAgreeMiddleware',  # Near the end of the list
        ...
    ]
    ```

* `django-letsagree` itself does not come with any migrations. It is recommended
    that you add migrations for its models in your project and avoid using the
    word `migrations` as the name of the folder.

    The relevant Django setting is [`MIGRATION_MODULES`](https://docs.djangoproject.com/en/dev/ref/settings/#migration-modules).
    In the following example, we will create a folder called `3p_migrations`
    in the main project folder where `settings.py` lies.

    If you wish to use a new folder, do not forget to create an empty `__init__.py` inside it.

    project/settings.py:
    ```python
        MIGRATION_MODULES = {
            'letsagree': 'project.3p_migrations.letsagree',
        }
    ```
    Then:
    ```python
        ./manage.py makemigrations letsagree
        ./manage.py migrate
    ```

* project/urls.py:

    ```python
    urlpatterns = [
            ...
            path('path/to/letsagree/', include('letsagree.urls')),
            ...
    ]
    ```

* Make sure [LANGUAGE_CODE](https://docs.djangoproject.com/en/dev/ref/settings/#language-code) is properly set as explained in the [Translation](#translation) section.

* [Sessions](https://docs.djangoproject.com/en/dev/topics/http/sessions/#enabling-sessions) should be enabled.


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

### Database queries


The middleware generates one database query per request in order to make sure that the user has agreed to all the terms related with the Group(s) he belongs to.

If `LETSAGREE_CACHE = True`, [Django's Cache Framework](https://docs.djangoproject.com/en/dev/topics/cache/) will be used and only one database query will be generated by the middleware, every 24 hours.

`LETSAGREE_CACHE` is not enabled by default, because it exposes the unique `id` for each user by creating a cache record with key `'letsagree-<user id>'`.

Tip: [django-hashid-field](https://github.com/nshafer/django-hashid-field), is a library that obscures unique `id`s, without compromising their uniqueness.

<a name='translation'></a>
### Translation


**Watch your `LANGUAGES`**!

#### Database

By default `lestagree` installs a tiny library [`django-translated-fields`](https://github.com/matthiask/django-translated-fields) to cater for translating the `title`, `summary` and `content` fields of the `Term` model. This library will create separate fields for each entry in the [`LANGUAGES`](https://docs.djangoproject.com/en/dev/ref/settings/#languages) list.

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

`LETSAGREE_CSS = {'all': ('letsagree/letsagree.css',)}`

Of course, one can completely [override the templates](https://docs.djangoproject.com/en/dev/howto/overriding-templates/).

In that case, bear in mind that if `{{ empty_form }}` is False, `{{ form }}` contains a formset.


### Other settings

* `LETSAGREE_LOGOUT_APP_NAME`: A logout link will appear in the top right corner of both templates.

  This is formed as `reverse(<LETSAGREE_LOGOUT_APP_NAME>:logout)`.

  The logout link defaults to `reverse('admin:logout')`.

* `LETSAGREE_BROWSER_TITLE`: A title for the default template.
* `LETSAGREE_BORDER_HEADER`: Text that will appear in the top left corner of the default template.


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



New Term Version
----------------
If two instances of Term associate with the same Group, the instance saved-last is the latest version. All logged in users have to provide consent for this latest version, independently of any previous consent they may have or have not given for the Terms associated with this Group.

`django-letsagree` takes into account if a logged-in user has provided consent only for the latest version of each Term associated with the Groups he belongs to. If not, the user can only logout or visit `django-letsagree` admin page retaining the right to delete any instances of consent he has provided.

Coverage: Not Included
-------------------------
* `LETSAGREE_CSS`
* `LETSAGREE_JS`
* `letsagree.admin.term_parents`
