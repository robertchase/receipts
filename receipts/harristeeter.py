from decimal import Decimal
import re

from receipts.item import Item


def is_receipt(data):
    if re.search("Harris Teeter", data):
        return True
    return False


def classify(data):
    """parse Items from harris teeter receipt data"""

    # remove newlines
    data = data.replace("\n", " ")

    # remove header
    header, body = re.split(r"VIC CUSTOMER \d* ", data, 1)

    # for each purchase
    while not body.startswith("**** "):  # start of footer
        if (m := re.match(r"PRICE YOU PAY \d+\.\d\d (.*)", body)):
            body = m.group(1)  # ignore this
        elif (m := re.match(r"TAX (\d+\.\d\d) (.*)", body)):
            tax, body = m.groups()
            yield Item("X", "TAX", Decimal(tax))
        elif (m := re.match(r"(.*?) (\d+\.\d\d)( |-)([A-Z]) (.*)", body)):
            desc, cost, sep, kind, body = m.groups()
            if desc.find("HOT FOODS") >= 0:
                kind = "F"  # food bar not considered grocery for tax purposes
            elif kind == "B":
                kind = "F"
            else:
                kind = "N"
            if sep == "-":  # discounted amount
                cost = sep + cost
            yield Item(kind, desc, Decimal(cost))
        elif (m := re.match(r"(.*) - (\d+\.\d\d) (.*)", body)):
            desc, cost, body = m.groups()
            yield Item("N", desc, Decimal(cost))

    if (s := re.search(r"BALANCE (\d+\.\d\d) ", body)):
        cost = s.group(1)
        yield Item("T", "Total", Decimal(cost))

    if (s := re.search(r"(\d\d)/(\d\d)/(\d\d) (.*)", body)):
        month, day, year, data = s.groups()
        yield Item("D", "Date", f"20{year}-{month}-{day}")


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    for i in items:
        print(i.kind, i.desc, i.value)
