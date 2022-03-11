
from copy import deepcopy
from boto3 import Session
from py import process
from apps.home.controllers.base import BaseController
from apps.home.controllers.owl_observability import OWLProfilingContoller
from apps.home.entities.models import Model
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
import django_tables2 as tables
from django.utils.html import format_html
import pandas as pd

class SearchOriginModelLinkColumn(tables.Column):
    def render(self, record):
        return format_html (f"<a href = \'/search/{record['project_name']} \' target='_blank'> {record['project_name']} </a>" )

class GitLinkColumn(tables.Column):
    def render(self, record):
        return format_html (f"<a href = \'{record['repo_url']} \' target='_blank'> {record['repo_url']} </a>" )
class ModelsTable(tables.Table):
    project_name = SearchOriginModelLinkColumn()
    # dag_name = tables.Column()
    # schedule = tables.Column()
    # catchup : tables.Column()
    # owner = tables.Column()
    created_at = tables.Column()
    last_release_ver = tables.Column()
    last_release_date = tables.Column()

    language = tables.Column()
    repo_url = GitLinkColumn()

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

    _pd_data: pd.DataFrame

    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None, monitoring=True):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=Model)
        self._profiling_controller = OWLProfilingContoller(session=session, configuration=configuration, document_adapter=document_adapter)
        self._table = ModelsTable
        self._feature_collection = None
        self._monitoring = monitoring


    def get_model(self, project_name, dag_name): 

        query_dict = deepcopy(self.QUERY_MODEL)
        query_dict["ExpressionAttributeValues"][":dag_name"] = dag_name
        query_dict["ExpressionAttributeValues"][":project_name"] = project_name
        results = self._document_adapter.query_custom_full(collection=self.COLLECTION, query_dict=query_dict)

        parsed_results = self._internal_parse(results)
        model = None
        if parsed_results and len(parsed_results) == 1:
            model = parsed_results[0]
        return model

    def get_models(self): 

        results = self._document_adapter.query_custom_full(collection=self.COLLECTION)

        self._internal_parse(results)

        return self._pd_data

    def _internal_parse(self, results):
        models = []
        parsed_results = []
        self._pd_data = pd.DataFrame()
        if results and len(results) > 0: 
            for result in results: 
                feature_metrics = None 

                result['metrics'] = []
                contributors = []
                for contributor in result['contributors']:
                    contributors.append({
                        'name': contributor[0], 
                        'login': contributor[1], 
                        'email': contributor[2], 
                    })
                
                dependencies = []
                process_type = ''
                for task in result['tasks'].values():
                    for k in task.keys():
                        if 'custom_tags' in k and 'ProcessType' in task['custom_tags']: 
                            process_type += task['custom_tags']['ProcessType'] + ' '
                        if 'dependencies' in k: 
                            for dep in task[k]:
                                dep_name = dep['table_name'] if type(dep) == dict else dep
                                if not self._monitoring:
                                    status_response = [] 
                                else: 
                                    status_response = self._profiling_controller.get_quality_status(dep_name.replace('.', '_'))

                                status =  ''
                                updated = ''
                                if len(status_response) > 0 and 'state' in status_response[0]:
                                    status = status_response[0]['state']
                                    updated = status_response[0]['updated_at']

                                dependencies.append({
                                    'type': k,
                                    'table_name': dep_name, 
                                    'status': status,
                                    'updated':updated, 
                                })
                                
                result['process_type'] = process_type
                result['contributors'] = contributors   
                result['dependencies'] = dependencies 
                parsed_results.append( result )
                models.append( self.parse_base_object(result) )
        self._data = pd.DataFrame(parsed_results).sort_values('last_release_date', ascending=False)

        return models

    def summary(self, columns, start_date=None, end_date=None, process_type=None):
        value = 0
        if not type(columns) == list:
            columns = [columns]

        if start_date and end_date: 
            data = self._data[self._data['created_at'].between(start_date, end_date)]
        else: 
            data = self._data

        if process_type: 
            data = data[self._data['process_type'].str.lower().str.contains(process_type)]

        count_results = data[columns].nunique()
        if len(count_results) > 0:
            value = count_results.values[0]
        else: 
            value = 0

        return value
    @property
    def profiling_controller(self):
        return self._profiling_controller
    
    @property
    def feature_collection(self):
        return self._feature_collection