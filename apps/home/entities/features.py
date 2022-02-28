from dataclasses import dataclass
from datetime import datetime
from typing import List

from apps.home.entities.metric import Metric

@dataclass
class Feature:
    origin : str
    name : str 
    desc : str
    type: str
    dag : str 
    source : str 
    schema : str
    metrics: List[Metric]
    updated_at : str 
    created_at : str 