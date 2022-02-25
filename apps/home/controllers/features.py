
from copy import deepcopy
from pytest import Session
from apps.home.controllers.base import BaseController
from apps.home.entities.features import Feature
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration


    
class FeaturesController(BaseController):
   

    COLLECTION = 'mlops_owl_fs_metadata_feature'



    QUERY_BY_ORIGIN_NAME = {
        "IndexName": "name-origin-index",
        "KeyConditionExpression": "#name = :name and #origin = :origin",
        "ExpressionAttributeNames": {"#name": "name", "#origin": "origin", },
        "ExpressionAttributeValues": {":name": {"S": ""}, ":origin": {"S": ""}},
    }

    
    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=Feature)


    

    def get_feature(self, name, origin): 

        query_dict = deepcopy(self.QUERY_BY_ORIGIN_NAME)
        query_dict["ExpressionAttributeValues"][":name"] = name
        query_dict["ExpressionAttributeValues"][":origin"] = origin
        results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)


        return self.parse_object(results)

        