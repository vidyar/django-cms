# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils import importlib
from django.db import models
import django

__all__ = ['User', 'get_user_model', 'user_model_label']

# Django 1.5+ compatibility
if django.VERSION >= (1, 5):
    from django.contrib.auth import get_user_model
    from django.contrib.auth.models import User as OriginalUser
    is_user_swapped = bool(OriginalUser._meta.swapped)
else:
    from django.contrib.auth.models import User
    User.USERNAME_FIELD = 'username'
    get_user_model = lambda: User
    is_user_swapped = False

user_model_label = getattr(settings, 'AUTH_USER_MODEL', 'auth.User')


# Some custom user models may require a custom UserAdmin class and associated forms,
# so provide ways to import them.
# For some reason, importing from django.contrib.auth.admin or using importlib
# magic at module level results in an circular imports in some contexts (like
# with WSGI or cms check).


def get_user_admin():
    custom_admin = _get_object_from_user_module("admin", "UserAdmin")
    if custom_admin:
        return custom_admin
    else:
        from django.contrib.auth.admin import UserAdmin
        return UserAdmin


def get_user_creation_form():
    custom_form = _get_object_from_user_module("forms", "UserCreationForm")
    if custom_form:
        return custom_form
    else:
        from django.contrib.auth.forms import UserCreationForm
        return UserCreationForm


def get_user_change_form():
    custom_form = _get_object_from_user_module("forms", "UserChangeForm")
    if custom_form:
        return custom_form
    else:
        from django.contrib.auth.forms import UserChangeForm
        return UserChangeForm


def _get_object_from_user_module(module_name, obj_name):
    """Return my_user_app.module_name.obj_name if it exists or None"""
    if is_user_swapped:
        user_app_name = user_model_label.split('.')[0]
        app = models.get_app(user_app_name)

        try:
            full_module_name = app.__name__[:-6] + module_name
            custom_module = importlib.import_module(full_module_name)
            return getattr(custom_module, obj_name, None)
        except ImportError:
            pass
    return None
