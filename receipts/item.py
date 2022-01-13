from dataclasses import dataclass
from decimal import Decimal
from typing import Union


@dataclass
class Item:
    kind: str
    desc: str
    value: Union[str, Decimal]
