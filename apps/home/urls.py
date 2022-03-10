# -*- encoding: utf-8 -*-

from django.urls import path, re_path
from apps.home import views

urlpatterns = [

    # The home page
    path('', views.index, name='home'),
    path('search/<str:term>', views.search, name='search'),
    path('search_type/<str:artifact_type>', views.search_type, name='search_type'),
    path('feature/<str:feature_origin>/<str:feature_name>', views.feature, name='feature'),
    path('model/<str:project_name>/<str:dag_name>', views.model, name='model'),
    path('feature_collection/<str:feature_origin>', views.feature_collection, name='feature_collection'),

    
    # Matches any html file
    re_path(r'^.*\.*\.html', views.pages, name='pages'),

]
