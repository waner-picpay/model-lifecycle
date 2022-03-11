
from copy import deepcopy
from boto3 import Session
from apps.home.controllers.base import BaseController
from apps.home.controllers.owl_observability import OWLProfilingContoller
from apps.home.entities.features import Feature, FeatureCollection
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
import django_tables2 as tables
from django.utils.html import format_html

class FeatureLinkColumn(tables.Column):
    def render(self, record):
        return format_html (f"<a href = \'/feature/{record['origin']}/{record['name']} \' target='_blank'> {record['origin']}.{record['name']} </a>" )

class ProfilingLinkColumn(tables.Column):
    def render(self, record):
        return format_html (f"<a href = \'{record['profile_link']}\' target='_blank'> Profile </a>" )


class FeaturesTable(tables.Table):
    origin  = tables.Column()
    name  = FeatureLinkColumn() 
    desc  = tables.Column()
    updated_at  = tables.Column() 
    created_at  = tables.Column() 

    class Meta:
        template_name="django_tables2/bootstrap-responsive.html"
        attrs = {'class' : 'table text-sm'}

class FeaturesController(BaseController):
   

    FEATURE_COLLECTION = 'mlops_owl_fs_metadata_feature'

    COLLECTION_FD = 'mlops_owl_fs_metadata_feature_dataset'
    COLLECTION_FG = 'mlops_owl_fs_metadata_feature_group'

    QUERY_FEATURE_BY_ORIGIN_NAME = {
        "IndexName": "name-origin-index",
        "KeyConditionExpression": "#name = :name and #origin = :origin",
        "ExpressionAttributeNames": {"#name": "name", "#origin": "origin", },
        "ExpressionAttributeValues": {":name": {"S": ""}, ":origin": {"S": ""}},
    }

    QUERY_FS_FD_BY_NAME = {
        "KeyConditionExpression": "#name = :name ",
        "ExpressionAttributeNames": {"#name": "name"},
        "ExpressionAttributeValues": {":name": {"S": ""}},
    }

    _profiling_controller: OWLProfilingContoller
    _feature_collection: FeatureCollection

    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=Feature)
        self._profiling_controller = OWLProfilingContoller(session=session, configuration=configuration, document_adapter=document_adapter)
        self._table = FeaturesTable
        self._feature_collection = None

    def get_feature_collection(self, name):
        query_dict = deepcopy(self.QUERY_FS_FD_BY_NAME)
        query_dict["ExpressionAttributeValues"][":name"] = name

        if 'fg_' in name:
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_FG, query_dict=query_dict)
            tp = 'FeatureGroup'
            schema = 'feature_store_groups'
        elif 'fd_' in name: 
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_FD, query_dict=query_dict)
            tp = 'FeatureDataset'
            schema = 'feature_store_datasets'
        else: 
            tp = 'Other'
            schema = 'name'

        if results and len(results) == 1: 
            
            results[0]['type'] = tp
            if 'is_online' not in results[0]:
                results[0]['is_online'] = False

            self._profiling_controller.get_last_run_profiling(schema, name)
            feature_collection = self.parse_base_object(results, FeatureCollection)
        self._feature_collection = feature_collection
        return feature_collection

    def get_feature(self, name, origin): 
        # if not self._feature_collection: 
        self.get_feature_collection(name=origin)
        feature = None
        query_dict = deepcopy(self.QUERY_FEATURE_BY_ORIGIN_NAME)
        query_dict["ExpressionAttributeValues"][":name"] = name
        query_dict["ExpressionAttributeValues"][":origin"] = origin
        results = self._document_adapter.query_custom_full(collection=self.FEATURE_COLLECTION, query_dict=query_dict)

        if results and len(results) == 1: 
               
            feature_metrics = self._profiling_controller.feature_metrics

            if name in feature_metrics: 
                results[0]['metrics'] = feature_metrics[name]
            else: 
                results[0]['metrics'] = []

            feature = self.parse_base_object(results)

        return feature

    def build_features_table(self):
        results = []
        for fvalue in self._feature_collection.features:
            fvalue['metrics'] = []
            if 'origin' not in fvalue: 
                fvalue['origin'] = self._feature_collection.name
            if not 'created_at' in fvalue: 
                fvalue['created_at'] = None
            
            if not 'updated_at' in fvalue: 
                fvalue['updated_at'] = None
            
            results.append(fvalue)
        return self.render_table(results)

    @property
    def profiling_controller(self):
        return self._profiling_controller
    
    @property
    def feature_collection(self):
        return self._feature_collection