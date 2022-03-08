
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
            return f"/models/{record['origin']}/{record['name']}"

class SearchOriginModelLinkColumn(tables.Column):
    def render(self, record):
        if record['artifact_type'] == 'Feature':
            return format_html (f"<a href = \'/feature_collection/{record['origin']} \' target='_blank'> {record['origin']} </a>" )
        else: 
            return f"/models/{record['origin']}"

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
   

    COLLECTION = 'mlops_owl_fs_metadata_feature'

    QUERY_BY_NAME = {
        "FilterExpression": "contains(#name , :name)",
        "ExpressionAttributeNames": {"#name": "name"},
        "ExpressionAttributeValues": {":name": {"S": ""}},
    }

    QUERY_BY_ORIGIN_NAME = {
        "IndexName": "name-origin-index",
        "KeyConditionExpression": "#name = :name and #origin = :origin",
        "ExpressionAttributeNames": {"#name": "name", "#origin": "origin", },
        "ExpressionAttributeValues": {":name": {"S": ""}, ":origin": {"S": ""}},
    }
    QUERY_BY_ORIGIN = {
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
            query_dict = deepcopy(self.QUERY_BY_ORIGIN_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            query_dict["ExpressionAttributeValues"][":origin"] = origin
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)
            if results: 
                all_results.extend(results)
            

        if name:
            query_dict = deepcopy(self.QUERY_BY_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)
            if results: 
                all_results.extend(results)

        if origin: 
            query_dict = deepcopy(self.QUERY_BY_ORIGIN)
            query_dict["ExpressionAttributeValues"][":origin"] = origin
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)
            if results: 
                all_results.extend(results)

        if not name and not origin: 
            query_dict = deepcopy(self.QUERY_TABLE)
            results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)
            if results: 
                all_results.extend(results)


        return self.render_table(all_results)

        