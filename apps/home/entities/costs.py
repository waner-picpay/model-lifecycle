from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ProcessTypeCost:
    tag:str
    amount:Decimal
    unit:str
    start_date: str
    end_date:str