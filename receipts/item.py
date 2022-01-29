from datetime import datetime
from decimal import Decimal, InvalidOperation


class Item:

    FOOD = "F"
    NON_FOOD = "N"
    TAX = "X"
    TOTAL = "T"
    DATE = "D"

    def __init__(self, kind, desc=None, value=None):
        self.kind = kind
        if self.kind == self.TAX:
            desc = "Tax"
        elif self.kind == self.TOTAL:
            desc = "Total"
        elif self.kind == self.DATE:
            desc = "Date"
        self.desc = desc
        self.value = value

    def __setattr__(self, name, value):
        if name == "kind":
            valid = (self.FOOD, self.NON_FOOD, self.TAX, self.TOTAL, self.DATE)
            if value not in valid:
                raise ValueError(f"{name} must be one of {valid}")
        elif name == "desc":
            if value is None:
                raise ValueError("desc cannot be None")
        elif name == "value":
            if self.kind == self.DATE:
                datetime.strptime(value, "%Y-%m-%d")  # just checking
            elif value is None:
                value = Decimal("0.00")
            else:
                try:
                    value = Decimal(value)
                except InvalidOperation as exc:
                    raise ValueError("invalid number") from exc
        else:
            raise AttributeError(name)

        self.__dict__[name] = value

    def __str__(self):
        if isinstance(self.value, Decimal):
            value = f"{self.value:>.2f}"
        else:
            value = self.value
        return (
            f"{self.kind}"
            f" {self.desc}"
            f" {value}"
        )
