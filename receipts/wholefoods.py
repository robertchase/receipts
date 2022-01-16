from decimal import Decimal
import re

from receipts.item import Item


def is_receipt(data):
    if re.search("WH.LE FOODS", data):
        return True
    return False


def classify(data):
    """parse Items from wholefoods receipt data"""

    # remove header
    _, data = re.split(r"WH.LE FOODS.*?MARKET\n.+?, [A-Z]{2} \d{5}.*?\n",
                       data, flags=re.DOTALL)

    # remove newlines
    body = data.replace("\n", " ")

    while (m := re.match(r"(^.*?) \$(\d+\.\d\d) (F?T) (.*)", body)):
        desc, cost, kind, body = m.groups()

        if desc.find("HOT BAR") >= 0:  # treat HOT BAR like food
            kind = "F"
        elif kind == "FT":
            kind = "F"
        else:
            kind = "N"

        yield Item(kind, desc, Decimal(cost))

        if (s := re.match(r"(\*Sale\*.+?)- ?\$(\d+\.\d\d) (.*)", body)):
            desc, discount, body = s.groups()
            yield Item(kind, desc, -Decimal(discount))

        if (s := re.match(r"(Prime Extra.+?)- ?\$(\d+\.\d\d) (.*)", body)):
            desc, discount, body = s.groups()
            yield Item(kind, desc, -Decimal(discount))

    while (s := re.search(r"(Tax:? \d\.\d\d%) \$(\d\.\d\d) (.*)", body)):
        desc, cost, body = s.groups()
        yield Item("X", "Tax", Decimal(cost))

    if (s := re.search(r"Total: +?\$(\d+\.\d\d) (.*)", body)):
        cost, body = s.groups()
        yield Item("T", "Total", Decimal(cost))

    if (s := re.search(r"(\d\d)/(\d\d)/(20\d\d) (.*)", body)):
        month, day, year, body = s.groups()
        yield Item("D", "Date", f"{year}-{month}-{day}")


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    for i in items:
        print(i.kind, i.desc, i.value)
