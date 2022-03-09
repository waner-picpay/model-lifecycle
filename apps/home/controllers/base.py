from abc import ABC
from ast import Dict
from typing import List, Type, Any
from xmlrpc.client import Boolean

import django_tables2 as tables
from boto3 import Session
from dataclasses import fields

import pandas as pd

import apps.home.controllers as controllers

from apps.home.store.interfaces import IDocumentAdapter

from apps.home.utils.configuration import Configuration
from apps.home.utils.metaclasses import SingletonMeta

class BaseTable(tables.Table):
    # select_column = tables.CheckBoxColumn(verbose_name='', empty_values=('NA',))

    class Meta:
        attrs = {'class' : 'table text-sm'}
        template_name="django_tables2/bootstrap-responsive.html"



class BaseController(metaclass=SingletonMeta):
    _session :Session
    _configuration :Configuration
    _document_adapter :IDocumentAdapter
    _data_klass:Type
    _table : Type
    _use_artifact_type:Boolean


    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None, data_klass:Type = None):
        
        if not session: 
            session = controllers.session
        
        if not configuration: 
            configuration = controllers.configuration
        
        if not document_adapter: 
            document_adapter = controllers.db_adapter

        self._session = session
        self._configuration = configuration
        self._document_adapter = document_adapter
        self._data_klass = data_klass
        self._use_artifact_type = False
        self._table = self._generate_table()


    def _generate_table(self) -> Type:
        if self._data_klass:
            attrs = {field.name: tables.Column() for field in fields(self._data_klass)}
            attrs['Meta'] = type('Meta', (), dict(attrs={"class":"paleblue", "orderable":"True", "width":"100%"}) )
            klass = type('DynamicTable', (BaseTable,), attrs)
            return klass

    def _parse_column_types(self, data:Dict, artifact_type:str = 'Feature' ):
        result = pd.DataFrame(data)
        for col in result.columns:
            if '_at' in col: 
                result[col] = pd.to_datetime(result[col],unit='s')
        if self._use_artifact_type: 
            if not artifact_type:
                result['artifact_type'] = self._data_klass.__name__
            else:
                result['artifact_type'] = artifact_type
        return result

    def render_table(self, data:Dict) -> Any: 
        records = self._parse_column_types(data).to_dict('records')
        return self._table(records)

    def parse_results(self, data:List):
        self._data = self._parse_column_types(data)

        return self._data

    def parse_base_object(self, data:Dict, data_klass:Type= None):
        result = None
        if not data_klass: 
            data_klass = self._data_klass
        if data: 
            row = data[0]
            dk_f = data_klass.__dataclass_fields__.keys()
            dt_f = row.keys()
            missing_fields = set(dk_f) - set(dt_f)
            for f in missing_fields: 
                row[f] = None
            result = data_klass(**row)
        return result