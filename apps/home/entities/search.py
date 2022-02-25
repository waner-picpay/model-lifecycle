from dataclasses import dataclass
from datetime import datetime

@dataclass
class SearchTerm:
    artifact_type: str
    origin : str
    name : str 
    desc : str
    dag : str 
    source : str 
    updated_at : str 
    created_at : str 