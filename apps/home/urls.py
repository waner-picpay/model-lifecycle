# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('search/<str:term>', views.search, name='search'),
    path('feature/<str:feature_origin>/<str:feature_name>', views.feature, name='feature'),
    # Matches any html file
    re_path(r'^.*\.*\.html', views.pages, name='pages'),

]
