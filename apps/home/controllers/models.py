
from copy import deepcopy
from boto3 import Session
from apps.home.controllers.base import BaseController
from apps.home.controllers.owl_observability import OWLProfilingContoller
from apps.home.entities.models import Model
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
import django_tables2 as tables
from django.utils.html import format_html


class ProfilingLinkColumn(tables.Column):
    def render(self, record):
        return format_html (f"<a href = \'{record['profile_link']}\' target='_blank'> Profile </a>" )


class ModelsTable(tables.Table):
    project_name = tables.Column()
    dag_name = tables.Column()
    schedule = tables.Column()
    catchup : tables.Column()
    owner = tables.Column()
    created_at = tables.Column()
    last_release : tables.Column()
    language = tables.Column()
    repo_url = tables.Column()

    class Meta:
        template_name="django_tables2/bootstrap-responsive.html"
        attrs = {'class' : 'table text-sm'}

class ModelsController(BaseController):
   

    COLLECTION = 'mlops_owl_models'

    QUERY_MODEL = {
        "KeyConditionExpression": "#dag_name = :dag_name and #project_name = :project_name",
        "ExpressionAttributeNames": {"#dag_name": "dag_name", "#project_name": "project_name", },
        "ExpressionAttributeValues": {":dag_name": {"S": ""}, ":project_name": {"S": ""}},
    }

    _profiling_controller: OWLProfilingContoller

    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=Model)
        self._profiling_controller = OWLProfilingContoller(session=session, configuration=configuration, document_adapter=document_adapter)
        self._table = ModelsTable
        self._feature_collection = None


    def get_model(self, project_name, dag_name): 

        query_dict = deepcopy(self.QUERY_MODEL)
        query_dict["ExpressionAttributeValues"][":dag_name"] = dag_name
        query_dict["ExpressionAttributeValues"][":project_name"] = project_name
        results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)

        if results and len(results) == 1: 
               
            feature_metrics = None #self._profiling_controller.feature_metrics

            # if dag_name in feature_metrics: 
            #     results[0]['metrics'] = feature_metrics[dag_name]
            # else: 
            results[0]['metrics'] = []
            contributors = []
            for contributor in results[0]['contributors']:
                contributors.append({
                    'name': contributor[0], 
                    'login': contributor[1], 
                    'email': contributor[2], 
                })
            results[0]['contributors'] = contributors   
            model = self.parse_base_object(results)

        return model

    # def build_features_table(self):
    #     results = []
    #     for fvalue in self._feature_collection.features:
    #         fvalue['metrics'] = []
    #         if 'origin' not in fvalue: 
    #             fvalue['origin'] = self._feature_collection.name
    #         results.append(fvalue)
    #     return self.render_table(results)

    @property
    def profiling_controller(self):
        return self._profiling_controller
    
    @property
    def feature_collection(self):
        return self._feature_collection