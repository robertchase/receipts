from datetime import datetime
from decimal import Decimal, InvalidOperation
import json


class Item:

    FOOD = "F"
    NON_FOOD = "N"
    TAX = "X"
    TOTAL = "T"
    DATE = "D"
    VENDOR = "V"
    SOURCE = "R"

    VALID_KIND = (FOOD, NON_FOOD, TAX, TOTAL, DATE, VENDOR, SOURCE)

    def __init__(self, kind, desc=None, value=None):
        self.kind = kind

        if default := {
                self.TAX: "Tax",
                self.TOTAL: "Total",
                self.DATE: "Date",
                self.VENDOR: "Vendor",
                self.SOURCE: "Source",
                }.get(self.kind):
            desc = default

        self.desc = desc
        self.value = value

    def __setattr__(self, name, value):
        if name == "kind":
            if value not in self.VALID_KIND:
                raise ValueError(f"{name} must be one of {self.VALID_KIND}")
        elif name == "desc":
            if value is None:
                raise ValueError("desc cannot be None")
        elif name == "value":
            if self.kind in (self.VENDOR, self.SOURCE):
                pass
            elif self.kind == self.DATE:
                datetime.strptime(value, "%Y-%m-%d")  # just checking
            elif value is None:
                value = Decimal("0.00")
            else:
                try:
                    value = Decimal(value)
                except InvalidOperation as exc:
                    raise ValueError(f"invalid number {value}") from exc
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

    def as_dict(self):
        return dict(
            kind=self.kind,
            desc=self.desc,
            value=f"{v:>.2f}" if isinstance(v := self.value, Decimal) else v
        )

    @classmethod
    def loads(cls, data):
        return cls(**json.loads(data))

    def dumps(self):
        return json.dumps(self.as_dict())
