
from copy import deepcopy
from typing import Dict
from pytest import Session
from apps.home.controllers.base import BaseController
from apps.home.controllers.owl_observability import OWLProfilingContoller
from apps.home.entities.features import Feature
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
import requests

    
class FeaturesController(BaseController):
   

    COLLECTION = 'mlops_owl_fs_metadata_feature'


    QUERY_BY_ORIGIN_NAME = {
        "IndexName": "name-origin-index",
        "KeyConditionExpression": "#name = :name and #origin = :origin",
        "ExpressionAttributeNames": {"#name": "name", "#origin": "origin", },
        "ExpressionAttributeValues": {":name": {"S": ""}, ":origin": {"S": ""}},
    }

    _profiling_controller: OWLProfilingContoller

    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=Feature)
        self._profiling_controller = OWLProfilingContoller(session=session, configuration=configuration, document_adapter=document_adapter)



    def get_feature(self, name, origin): 
        feature = None
        query_dict = deepcopy(self.QUERY_BY_ORIGIN_NAME)
        query_dict["ExpressionAttributeValues"][":name"] = name
        query_dict["ExpressionAttributeValues"][":origin"] = origin
        results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)

        if results and len(results) == 1: 
            schema = results[0]['origin']
            if 'fd_' in schema: 
                results[0]['schema'] = 'feature_store_datasets'
            elif 'fg_' in schema: 
                results[0]['schema'] = 'feature_store_groups'
            else: 
                results[0]['schema'] = schema

            self._profiling_controller.get_last_run_profiling(results[0]['schema'], origin)
            feature_metrics = self._profiling_controller.feature_metrics

            if name in feature_metrics: 
                results[0]['metrics'] = feature_metrics[name]
            else: 
                results[0]['metrics'] = []

            feature = self.parse_object(results)

        return feature

    @property
    def profiling_controller(self):
        return self._profiling_controller