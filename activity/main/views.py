from django.utils.translation import gettext_lazy as _
from django.http import HttpResponseNotFound
from django.shortcuts import render


def index(request):
    return render(request, "main/index.html", {"title": "Index"})


def page_not_found(request, exception):
    return HttpResponseNotFound("Error 404")
