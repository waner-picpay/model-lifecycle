# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from asyncio.log import logger
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, render

from apps.home.controllers.search import SearchController
from apps.home.utils import serialization


@login_required(login_url="/login/")
def index(request):
    context = {'segment': 'index'}

    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))


@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split('/')[-1]

        if load_template == 'admin':
            return HttpResponseRedirect(reverse('admin:index'))
        context['segment'] = load_template

        html_template = loader.get_template('home/' + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template('home/page-500.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def search(request, term):
    
    feature_origin = term
    feature_name = term

    context = {'segment':'Search'}

    try: 
        controller = SearchController()
       
        table = controller.get_features(name=feature_name, origin=feature_origin, offset=None)
        context['results_table'] = table

        return render(request=request, template_name='home/search.html', context=context)
    except KeyError as error: 
        logger.error(f'Key error home.views.search {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))