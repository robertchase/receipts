from decimal import Decimal
import json

from receipts.classify import classify


def summary(items):
    food = non_food = tax = Decimal("0.00")
    for item in items:
        if item.kind == "F":
            food += item.value
        elif item.kind == "N":
            non_food += item.value
        elif item.kind == "X":
            tax += item.value
        elif item.kind == "T":
            total = item.value
        elif item.kind == "D":
            date = item.value

    if total != (calculated := food + non_food + tax):
        raise Exception(
            f"total ({total}) does not match sum of items ({calculated})")

    return dict(
        date=date,
        total=total,
        food=food,
        non_food=non_food,
        tax=tax,
    )


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    class ItemDecoder(json.JSONEncoder):
        def default(self, obj):
            if isinstance(obj, Decimal):
                return str(obj)
            return json.JSONEncoder.default(self, obj)

    items = classify(data)
    print(json.dumps(summary(items), cls=ItemDecoder))
