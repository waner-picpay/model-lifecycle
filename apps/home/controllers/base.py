from abc import ABC
from ast import Dict
import re
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



class BaseController():
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
        self._data = None

    def _generate_table(self) -> Type:
        if self._data_klass:
            attrs = {field.name: tables.Column() for field in fields(self._data_klass)}
            attrs['Meta'] = type('Meta', (), dict(attrs={"class":"paleblue", "orderable":"True", "width":"100%"}) )
            klass = type('DynamicTable', (BaseTable,), attrs)
            return klass

    def _parse_column_types(self, data:Dict, artifact_type:str = 'Feature' ):
        def date_convertion(value):
            if value:
                if re.match(r'\d{4}\-(0?[1-9]|1[012])\-(0?[1-9]|[12][0-9]|3[01])', value):
                        value = pd.to_datetime(value)
                else:
                    value = pd.to_datetime(value,unit='s')
            return value
        result = pd.DataFrame(data)
        for col in result.columns:
            if '_at' in col: 
                result[col] = result[col].apply(date_convertion)
                
                    
        return result

    def render_table(self, data:Dict = None) -> Any: 
        records = []
        if data is not None:
            self._data = self._parse_column_types(data)
        elif self._data is None: 
            return self._table([])
        records = self._data[list(self._table.base_columns.keys())].drop_duplicates().to_dict('records')
        return self._table(records)

    def parse_results(self, data:List):
        self._data = self._parse_column_types(data)

        return self._data

    def parse_base_object(self, data:Dict, data_klass:Type= None):
        result = None
        if type(data) == list: 
            data = data[0]
        if not data_klass: 
            data_klass = self._data_klass
        if data: 
            row = data
            dk_f = data_klass.__dataclass_fields__.keys()
            dt_f = row.keys()
            missing_fields_klass = set(dk_f) - set(dt_f)
            missing_fields_dict = set(dt_f) - set(dk_f)
            for f in missing_fields_klass: 
                row[f] = None
            for k in missing_fields_dict:
                del row[k]
            result = data_klass(**row)
        return result