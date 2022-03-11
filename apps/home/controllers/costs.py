import boto3

from copy import deepcopy
from typing import Dict, List, Type
from boto3 import Session
from apps.home.controllers.base import BaseController
from apps.home.entities.costs import ProcessTypeCost
from apps.home.factories.logger import LoggerFactory
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
from urllib.parse import quote_plus as urlencode
logger = LoggerFactory.get_logger(__name__)
class CostsExplorer(BaseController):
    __SELECTED_PROCESS_TYPES = [
                        'ProcessType$DataPrep',
                        'ProcessType$DataProcessing',
                        'ProcessType$PreProcess',
                        'ProcessType$Predict',
                        'ProcessType$Preprocessing',
                        'ProcessType$Train',
                        'ProcessType$predict',
                        'ProcessType$train',
    ]
    _total_costs_period:float
    _start_date:str
    _end_date:str
                    
    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter = None, data_klass: Type = ProcessTypeCost):
        super().__init__(session, configuration, document_adapter, data_klass)
        self._client = boto3.client('ce')

    @property
    def total_costs_period(self) -> float: 
        return self._total_costs_period

    def _get_aws_costs_usage(self, start_date:str, end_date:str, tag_type:str):
        self._start_date = start_date
        self._end_date = end_date
        response = self._client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
           
            Metrics=[
                'BLENDED_COST',
            ],
            GroupBy=[
                {
                    'Type': 'TAG',
                    'Key': tag_type
                },
            ]
        )
        return response
        
    def get_costs_usage_process(self, start_date:str, end_date:str):
        tag_type = 'ProcessType'
        response = self._get_aws_costs_usage(start_date, end_date, tag_type)
        results = []
        self._total_costs_period = 0.0
        if len(response['ResultsByTime']) > 0:
            start_date = response['ResultsByTime'][0]['TimePeriod']['Start']
            end_date = response['ResultsByTime'][0]['TimePeriod']['End']
            for group in response['ResultsByTime'][0]['Groups']:
                group_key = group['Keys'][0]
                if group_key in  self.__SELECTED_PROCESS_TYPES:
                    cost_dict = group['Metrics']['BlendedCost']
                    amount = float(int(float(cost_dict['Amount']) * 1000) / 1000.00)    
                    results.append({
                        'tag':group_key, 
                        'amount':f'{amount:.2f}', 
                        'unit':cost_dict['Unit'], 
                        'start_date': start_date, 
                        'end_date':end_date})
                    self._total_costs_period += float(amount)
                
        self.parse_results(results)           
        return response

    def get_costs_usage_project(self, start_date:str, end_date:str, project_name:str):
        tag_type = 'Project'
        response = self._get_aws_costs_usage(start_date, end_date, tag_type)
        result = {}
        self._total_costs_period = 0.0
        if len(response['ResultsByTime']) > 0:
            start_date = response['ResultsByTime'][0]['TimePeriod']['Start']
            end_date = response['ResultsByTime'][0]['TimePeriod']['End']
            for group in response['ResultsByTime'][0]['Groups']:
                group_key = group['Keys'][0]
                if group_key  == f'Project${project_name}':
                    cost_dict = group['Metrics']['BlendedCost']
                    amount = float(int(float(cost_dict['Amount']) * 1000) / 1000.00)    
                    result = {
                        'tag':group_key, 
                        'amount':f'{amount:.2f}', 
                        'unit':cost_dict['Unit'], 
                        'start_date': start_date, 
                        'end_date':end_date}
                    self._total_costs_period += float(amount)

    def get_costs_usage_projects(self, start_date:str, end_date:str):
        tag_type = 'Project'
        response = self._get_aws_costs_usage(start_date, end_date, tag_type)
        result = {}
        results = []
        self._total_costs_period = 0.0
        if len(response['ResultsByTime']) > 0:
            start_date = response['ResultsByTime'][0]['TimePeriod']['Start']
            end_date = response['ResultsByTime'][0]['TimePeriod']['End']
            for group in response['ResultsByTime'][0]['Groups']:
                group_key = group['Keys'][0]
                # if group_key  == f'Project${project_name}':
                cost_dict = group['Metrics']['BlendedCost']
                amount = float(int(float(cost_dict['Amount']) * 1000) / 1000.00)    
                result = {
                    'tag':group_key, 
                    'amount':f'{amount:.2f}', 
                    'unit':cost_dict['Unit'], 
                    'start_date': start_date, 
                    'end_date':end_date}
                self._total_costs_period += float(amount)
                results.append(result)

        self.parse_results(results)           
        return response

    def build_table(self):
        return self.render_table(self._data)