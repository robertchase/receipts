from decimal import Decimal
import json

from receipts.classify import classify
from receipts.item import Item


def summary(items):
    sum = {Item.FOOD: Decimal("0.00"), Item.NON_FOOD: Decimal("0.00")}
    for item in items:
        if isinstance(item.value, Decimal):
            if item.kind not in sum:
                sum[item.kind] = Decimal("0.00")
            sum[item.kind] += item.value
        else:
            sum[item.kind] = item.value

    if (total := sum[Item.TOTAL]) != (
            calculated := sum.get(Item.FOOD) +
            sum.get(Item.NON_FOOD) +
            sum[Item.TAX]):
        raise Exception(
            f"total ({total}) does not match sum of items ({calculated})")

    return {Item.KIND_NAMES[key]: sum.get(key) for key in Item.VALID_KIND}


if __name__ == "__main__":
    import os
    import sys

    for path in sys.argv[1:]:

        with open(path) as source:
            data = source.read()

        name = os.path.split(path)[1]

        class ItemDecoder(json.JSONEncoder):
            def default(self, obj):
                if isinstance(obj, Decimal):
                    return str(obj)
                return json.JSONEncoder.default(self, obj)

        items = classify(data, source=name)
        print(json.dumps(summary(items), cls=ItemDecoder))
