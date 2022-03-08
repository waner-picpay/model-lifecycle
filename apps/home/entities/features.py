from dataclasses import dataclass
from typing import List, Dict

from apps.home.entities.metric import Metric

@dataclass
class FeatureCollection: 
    type: str
    name: str
    updated_at: str
    key_attr: str
    repo: str
    created_at: str
    owner: List[str]
    entities: List[str]
    is_online:bool
    features:Dict


@dataclass
class Feature:
    origin : str
    name : str 
    desc : str
    type: str
    dag : str 
    source : str 
    metrics: List[Metric]
    updated_at : str 
    created_at : str 