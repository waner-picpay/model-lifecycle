# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from asyncio.log import logger
import calendar
from datetime import datetime, timedelta
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404, render
from apps.home.controllers.costs import CostsExplorer
from apps.home.controllers.features import FeaturesController
from apps.home.controllers.models import ModelsController

from apps.home.controllers.search import SearchController


def index(request):
    context = {'segment': 'index'}
    ce = CostsExplorer()
    current_date = datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    first_day = current_date.replace(day=1)
    last_period_date = first_day - timedelta(days=1)
    last_period_month = last_period_date.month
    last_period_year = last_period_date.year

    start_date, end_date = get_dates(last_period_year, last_period_month)
    ce.get_costs_usage_process(start_date, end_date)
    context['processes_last_costs_table'] = ce.build_processes_table()
    context['last_costs'] = f'$ {ce.total_costs_period:0.2f}'
    last_costs = ce.total_costs_period

    start_date, end_date = get_dates(current_year, current_month)
    ce.get_costs_usage_process(start_date, end_date)
    context['processes_costs_table'] = ce.build_processes_table()
    context['current_costs'] = f'$ {ce.total_costs_period:0.2f}'
    costs_delta = (ce.total_costs_period / last_costs)*100
    costs_delta_positive = costs_delta < 100.0
    context['costs_delta'] =  f'{costs_delta:0.2f} %'
    context['costs_delta_positive'] = costs_delta_positive
    html_template = loader.get_template('home/index.html')
    return HttpResponse(html_template.render(context, request))

def get_dates(current_year, current_month):
    first_day, last_day = calendar.monthrange(current_year, current_month)
    start_date = f'{current_year}-{current_month:02d}-{first_day:02d}'
    end_date = f'{current_year}-{current_month:02d}-{last_day:02d}'
    return start_date,end_date


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

def search_type(request, artifact_type):
    
    context = {'segment':'Search'}

    try: 
        controller = SearchController()
       
        # table = controller.search_objects(name=feature_name, origin=feature_origin, offset=None)
        # context['results_table'] = table

        return render(request=request, template_name='home/search.html', context=context)
    except KeyError as error: 
        logger.error(f'Key error home.views.search {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

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
        logger.error(f'Key error home.views.feature {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))


def model(request, project_name, dag_name):
    

    context = {'segment':'Model', 'project_name':project_name, 'model_name':dag_name}

    try: 
        controller = ModelsController()
       
        model = controller.get_model(dag_name=dag_name, project_name=project_name)
        context['model'] = model
        context['profiling_url'] = controller.profiling_controller.get_url(feature_name=dag_name)
        return render(request=request, template_name='home/models.html', context=context)

    except KeyError as error: 
        logger.error(f'Key error home.views.model {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))

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
        logger.error(f'Key error home.views.feature_collection {error}')
        html_template = loader.get_template('home/page-404.html')
        return HttpResponse(html_template.render(context, request))