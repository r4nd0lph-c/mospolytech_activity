from django.utils.translation import gettext_lazy as _
from django.contrib import admin

from main.views import Auth, logout_user

admin.site.site_title = _("Activity")
admin.site.site_header = _("Mospolytech Activity")
admin.site.index_title = _("Administration")

admin.site.login = Auth.as_view()
admin.site.logout = logout_user
