from copy import deepcopy
import re
from typing import Dict, List
from pytest import Session
from apps.home.controllers.base import BaseController
from apps.home.entities.features import Feature
from apps.home.entities.metric import Metric
from apps.home.factories.logger import LoggerFactory
from apps.home.store.interfaces import IDocumentAdapter
from apps.home.utils.configuration import Configuration
import requests

logger = LoggerFactory.get_logger(__name__)
class OWLProfilingContoller(BaseController):


    SERVICE_URL = 'http://owl.ms.prod/v1/'
    
    SERVICE_URL_LAST_RUN = f'{SERVICE_URL}/run/getLast'

    _json_data:Dict

    _feature_metrics: Dict[str,List[Metric]]

    _project_name:str
    _experiment_name:str
    _stage_name:str
    _end_time:str
    _run_id:str
    _run_name:str

    

    def __init__(self, session: Session = None, configuration: Configuration = None, document_adapter: IDocumentAdapter= None):
        super().__init__(session=session, configuration=configuration, document_adapter=document_adapter, data_klass=None)
        self._feature_metrics = {}
        self._project_name = ''
        self._experiment_name = ''
        self._stage_name = ''
        self._end_time = ''
        self._run_id = ''
        self._run_name = ''

    def _parse_json_data(self): 
        feature_metrics = {}
        stage_name = ''
        for s, stage in self._json_data['stages'].items(): 
            if 'Statistics for' in s and  stage['stage_internal_name'] == 'Initial':
                stage_name = s
                if s in self._json_data['metrics_validation']:
                    validation_rules = self._json_data['metrics_validation'][s]
                else: 
                    validation_rules = {}
                for m, mvalue in stage['metrics_values'].items():
                    for f, fvalue in mvalue.items():
                        if f not in feature_metrics: 
                            feature_metrics[f] = []
                        validation_rule = ''
                        is_valid = True
                        if m in validation_rules and f in validation_rules[m]['columns']:
                            validation_rule = validation_rules[m]['validation_rule']
                            is_valid = validation_rules[m]['columns'][f]
                        
                        feature_metrics[f].append(Metric(m, fvalue, validation_rule, is_valid))
        self._feature_metrics = feature_metrics

        self._project_name = self._json_data['project_name']
        self._experiment_name = self._json_data['experiment_name']
        self._stage_name = stage_name
        self._end_time = self._json_data['end_time']

        self._run_name = self._json_data['run_name']

        try:
            run_id = re.search('(?<=uuid\().*?(?=\))', self._run_name).group(0)
        except AttributeError:
            run_id = '' 
        self._run_id = run_id



    def get_last_run_profiling(self, schema, origin):
        json_data = {}
        try:
            base_url  = f"{self.SERVICE_URL_LAST_RUN}/gov_{schema}_simple/Profiling%20{origin}"
            response = requests.get(base_url)
            json_data = response.json()
            self._json_data = json_data
            self._parse_json_data()
    
        except Exception as e: 
            logger.error(f"Error while reading owl observability ms {e}")
        return json_data


    def get_url(self, feature_name): 
        url = f"http://owl.dash.ms.prod/projects?project={self._project_name}&experiment={self._experiment_name}&run={self._run_id}&stage={self._stage_name}&feature={feature_name}&tab=Initial"       
        return url
        
    @property
    def feature_metrics (self) -> Dict[str,List[Metric]]:
        return self._feature_metrics