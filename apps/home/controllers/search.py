
from copy import deepcopy
import django_tables2 as tables
from boto3 import Session
from apps.home.controllers.base import BaseController
from apps.home.entities.search import SearchTerm
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
from django.utils.html import format_html

class SearchFeatureModelLinkColumn(tables.Column):
    def render(self, record):
        if record['artifact_type'] == 'Feature':
            return format_html (f"<a href = \'/feature/{record['origin']}/{record['name']} \' target='_blank'> {record['origin']}.{record['name']} </a>" )
        else: 
            return format_html (f"<a href = \'/model/{record['origin']}/{record['name']} \' target='_blank'> {record['origin']}.{record['name']} </a>" )

class SearchOriginModelLinkColumn(tables.Column):
    def render(self, record):
        if record['artifact_type'] == 'Feature':
            return format_html (f"<a href = \'/feature_collection/{record['origin']} \' target='_blank'> {record['origin']} </a>" )
        else: 
            return format_html (f"<a href = \'/search/{record['origin']} \' target='_blank'> {record['origin']}.{record['name']} </a>" )

class SearchTable(tables.Table):
    artifact_type = tables.Column()
    origin  = SearchOriginModelLinkColumn()
    name  = SearchFeatureModelLinkColumn() 
    desc  = tables.Column()
    dag  = tables.Column() 
    source  = tables.Column() 
    updated_at  = tables.Column() 
    created_at  = tables.Column() 

    class Meta:
        template_name="django_tables2/bootstrap-responsive.html"
        attrs = {'class' : 'table text-sm'}
        
class SearchController(BaseController):
   

    COLLECTION_FEATURES = 'mlops_owl_fs_metadata_feature'
    COLLECTION_MODELS = 'mlops_owl_models'

    QUERY_MODEL_NAME = {
        "FilterExpression": "contains(#name , :name)",
        "ExpressionAttributeNames": {"#name": "project_name"},
        "ExpressionAttributeValues": {":name": {"S": ""}},
    }
    
    QUERY_MODEL_DAG_NAME = {
        "IndexName":"dag_name-project_name-index",
        "FilterExpression": "contains(#name , :name)",
        "ExpressionAttributeNames": {"#name": "dag_name"},
        "ExpressionAttributeValues": {":name": {"S": ""}},
    }

    QUERY_FEATURE_NAME = {
        "FilterExpression": "contains(#name , :name)",
        "ExpressionAttributeNames": {"#name": "name"},
        "ExpressionAttributeValues": {":name": {"S": ""}},
    }

    QUERY_FEATURE_ORIGIN_NAME = {
        "IndexName": "name-origin-index",
        "KeyConditionExpression": "#name = :name and #origin = :origin",
        "ExpressionAttributeNames": {"#name": "name", "#origin": "origin", },
        "ExpressionAttributeValues": {":name": {"S": ""}, ":origin": {"S": ""}},
    }
    QUERY_FEATURE_ORIGIN = {
        "FilterExpression": "contains(#origin, :origin)",
        "ExpressionAttributeNames": {"#origin": "origin", },
        "ExpressionAttributeValues": {":origin": {"S": ""}},
    }
    QUERY_TABLE = {
    }

    
    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=SearchTerm)
        self._use_artifact_type = True
        self._table = SearchTable


    def search_objects(self, name=None, origin=None, offset=None): 
        all_results = []

        if name and origin: 
            query_dict = deepcopy(self.QUERY_FEATURE_ORIGIN_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            query_dict["ExpressionAttributeValues"][":origin"] = origin
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_FEATURES, query_dict=query_dict)
            self.extend_results(all_results, results, 'Feature')
            

        if name:
            query_dict = deepcopy(self.QUERY_FEATURE_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_FEATURES, query_dict=query_dict)
            
            self.extend_results(all_results, results, 'Feature')

            query_dict = deepcopy(self.QUERY_MODEL_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_MODELS, query_dict=query_dict)

            self.extend_results(all_results, results, 'Model')


            query_dict = deepcopy(self.QUERY_MODEL_DAG_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_MODELS, query_dict=query_dict)

            self.extend_results(all_results, results, 'Model')

        if origin: 
            query_dict = deepcopy(self.QUERY_FEATURE_ORIGIN)
            query_dict["ExpressionAttributeValues"][":origin"] = origin
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_FEATURES, query_dict=query_dict)
            self.extend_results(all_results, results, 'Feature')

        if not name and not origin: 
            query_dict = deepcopy(self.QUERY_TABLE)
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION_FEATURES, query_dict=query_dict)
            self.extend_results(all_results, results, 'Feature')
                

        return self.render_table(all_results)

    def extend_results(self, all_results, results, artifact_type):
        if results:
            for r in results:
                r['artifact_type'] = artifact_type
                if artifact_type == 'Model':
                    r['origin']  = r['project_name']
                    r['name']  =  r['dag_name']
                    r['desc']  = r['last_release']
                    r['dag']  = r['dag_name']
                    r['source']  = r['repo_url']
                    r['updated_at']  = r['last_release'][1]

            all_results.extend(results)
        self._raw_data = all_results

        