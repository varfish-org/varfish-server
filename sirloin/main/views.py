from django.shortcuts import render, redirect
from django.views.generic import TemplateView, FormView, RedirectView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages


class MainView(FormView):
    template_name = 'main/main.html'
    success_url = '.'