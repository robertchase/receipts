from decimal import Decimal
import json

from receipts.classify import classify
from receipts.item import Item


def summary(items):
    food = non_food = tax = Decimal("0.00")
    vendor = source = None
    for item in items:
        if item.kind == Item.FOOD:
            food += item.value
        elif item.kind == Item.NON_FOOD:
            non_food += item.value
        elif item.kind == Item.TAX:
            tax += item.value
        elif item.kind == Item.TOTAL:
            total = item.value
        elif item.kind == Item.DATE:
            date = item.value
        elif item.kind == Item.VENDOR:
            vendor = item.value
        elif item.kind == Item.SOURCE:
            source = item.value

    if total != (calculated := food + non_food + tax):
        raise Exception(
            f"total ({total}) does not match sum of items ({calculated})")

    return dict(
        date=date,
        total=total,
        food=food,
        non_food=non_food,
        tax=tax,
        vendor=vendor,
        source=source,
    )


if __name__ == "__main__":
    import os
    import sys

    for name in sys.argv[1:]:

        with open(name) as source:
            data = source.read()

        source_name = os.path.split(name)[1]

        class ItemDecoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                return json.JSONEncoder.default(self, obj)

        items = classify(data, source=source_name)
        print(json.dumps(summary(items), cls=ItemDecoder))
