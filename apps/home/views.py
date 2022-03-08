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
from apps.home.controllers.features import FeaturesController

from apps.home.controllers.search import SearchController


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
       
        table = controller.search_objects(name=feature_name, origin=feature_origin, offset=None)
        context['results_table'] = table

        return render(request=request, template_name='home/search.html', context=context)
    except KeyError as error: 
        logger.error(f'Key error home.views.search {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def feature(request, feature_origin, feature_name):
    

    context = {'segment':'Feature', 'feature_origin':feature_origin, 'feature_name':feature_name}

    try: 
        controller = FeaturesController()
       
        feature = controller.get_feature(name=feature_name, origin=feature_origin)
        context['feature'] = feature
        context['feature_collection'] = controller.feature_collection
        context['profiling_url'] = controller.profiling_controller.get_url(feature_name=feature_name)
        return render(request=request, template_name='home/features.html', context=context)
    except KeyError as error: 
        logger.error(f'Key error home.views.search {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

@login_required(login_url="/login/")
def feature_collection(request, feature_origin):
    
    context = {'segment':'Feature Collection', 'feature_origin':feature_origin}

    try: 
        controller = FeaturesController()
       
        feature_collection = controller.get_feature_collection(name=feature_origin)
        context['feature_collection'] = feature_collection
        context['profiling_url'] = controller.profiling_controller.get_url(feature_name='count')
        context['features_table'] = controller.build_features_table()
        return render(request=request, template_name='home/feature_collection.html', context=context)

    except KeyError as error: 
        logger.error(f'Key error home.views.search {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))