from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Model:
    project_name : str
    dag_name : str
    schedule : str
    catchup : bool
    owner : str
    tasks : dict
    created_at : str
    contributors : list
    last_release : tuple
    language : str
    repo_url : str
    dependencies: list
    first_execution_date: str
    type: str
    metrics: str