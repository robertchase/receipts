from decimal import Decimal

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

    if total != (calculated := food + non_food + tax):
        raise Exception(
            f"total ({total}) does not match sum of items ({calculated})")

    return dict(
        total=str(total),
        food=str(food),
        non_food=str(non_food),
        tax=str(tax),
    )


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    print(summary(items))
