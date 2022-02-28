from dataclasses import dataclass
from datetime import datetime

from black import Any

@dataclass
class Metric: 
    name: str
    value: str
    validation_rule: str
    is_valid: bool