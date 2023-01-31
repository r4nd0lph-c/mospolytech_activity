from dal import autocomplete

from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import *


class AuthForm(AuthenticationForm):
    username = forms.CharField(
        label=_("Username"),
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "*"
            }
        )
    )
    password = forms.CharField(
        label=_("Password"),
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "style": "border-right:0px;",
                "placeholder": "*"
            }
        )
    )
    remember_me = forms.BooleanField(
        label=_("Remember me?"),
        required=False,
        initial=True,
        widget=forms.CheckboxInput(
            attrs={
                "class": "form-check-input me-1",
                "type": "checkbox"
            }
        )
    )


class GroupSelect2Form(forms.Form):
    groups = forms.ModelChoiceField(
        queryset=StudyGroup.objects.filter(is_active=True).order_by("name"),
        widget=autocomplete.ModelSelect2(url="group_auto_complete"),
    )
