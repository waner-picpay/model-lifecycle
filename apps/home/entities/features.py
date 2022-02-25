from dataclasses import dataclass
from datetime import datetime

@dataclass
class Feature:
    origin : str
    name : str 
    desc : str
    type: str
    dag : str 
    source : str 
    updated_at : str 
    created_at : str 