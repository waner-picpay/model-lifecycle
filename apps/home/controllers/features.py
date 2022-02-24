
from copy import deepcopy
from pytest import Session
from apps.home.controllers.base import BaseController
from apps.home.entities.features import Feature
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration


class FeaturesController(BaseController):
   

    COLLECTION = 'mlops_owl_fs_metadata_feature'

    QUERY_BY_NAME = {
        "IndexName": COLLECTION,
        "KeyConditionExpression": "begins_with(#name , :name)",
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
        # "TableName": COLLECTION,
        "KeyConditionExpression": "#origin = :origin",
        "ExpressionAttributeNames": {"#origin": "origin", },
        "ExpressionAttributeValues": {":origin": {"S": ""}},
    }
    QUERY_TABLE = {
    }

    
    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=Feature)


    def get_features(self, name=None, origin=None, offset=None): 
        if name and origin: 
            query_dict = deepcopy(self.QUERY_BY_ORIGIN_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
            query_dict["ExpressionAttributeValues"][":origin"] = origin
        elif name and not origin:
            query_dict = deepcopy(self.QUERY_BY_NAME)
            query_dict["ExpressionAttributeValues"][":name"] = name
        elif not name and origin: 
            query_dict = deepcopy(self.QUERY_BY_ORIGIN)
            query_dict["ExpressionAttributeValues"][":origin"] = origin
        else: 
            query_dict = deepcopy(self.QUERY_TABLE)

        if offset: 
            query_dict["ExclusiveStartKey"] = offset

        result = self._document_adapter.query_custom(collection=self.COLLECTION, query_dict=query_dict)
        if result: 
            result, offset = result
        return self.render_table(result)
        