import boto3

from copy import deepcopy
from typing import Dict, List, Type
from boto3 import Session
from apps.home.controllers.base import BaseController
from apps.home.entities.metric import Metric
from apps.home.factories.logger import LoggerFactory
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
from urllib.parse import quote_plus as urlencode
logger = LoggerFactory.get_logger(__name__)
class CostsExplorer(BaseController):
    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter = None, data_klass: Type = None):
        super().__init__(session, configuration, document_adapter, data_klass)
        self._client = boto3.client('ce')

    def get_costs_usage(self, start_date:str, end_date:str):
        response = self._client.get_cost_and_usage(
            TimePeriod={
                'Start': start_date,
                'End': end_date
            },
            Granularity='MONTHLY',
            # Filter={
                
            #     'Tags': {
            #         'Key': 'ProcessType',
            #         'Values': [
            #             'string',
            #         ]
            #     }
            # },
            Metrics=[
                'BLENDED_COST',
            ],
            GroupBy=[
                {
                    'Type': 'TAG',
                    'Key': 'ProcessType'
                },
            ]
        )
        return response


ce = CostsExplorer()

print(ce.get_costs_usage())