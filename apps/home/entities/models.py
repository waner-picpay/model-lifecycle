from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Model:
    project_name : str
    dag_name : str
    process_type:str
    schedule : str
    catchup : bool
    owner : str
    tasks : dict
    created_at : str
    start_date: str
    contributors : list
    last_release_ver:str
    last_release_date: str
    language : str
    repo_url : str
    dependencies: list
    first_execution_date: str
    type: str
    metrics: str