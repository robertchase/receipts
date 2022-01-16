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
    header, data = re.split(r"VIC CUSTOMER \d* ", data, 1)

    # remove footer
    data, footer = re.split(r" \*\*\*\* ", data, 1)

    # for each purchase
    for desc, cost, kind in receipt_items(data):
        yield Item(kind, desc, Decimal(cost))

    if (s := re.match(r"BALANCE (\d+\.\d\d) ", footer)):
        cost = s.group(1)
        yield Item("T", "Total", Decimal(cost))

    if (s := re.search(r"(\d\d)/(\d\d)/(\d\d) (.*)", footer)):
        month, day, year, data = s.groups()
        yield Item("D", "Date", f"20{year}-{month}-{day}")


def receipt_items(body):
    while body:
        if (m := re.match(r"PRICE YOU PAY \d+\.\d\d (.*)", body)):
            body = m.group(1)  # ignore
        elif (m := re.match(r"TAX (\d+\.\d\d)()", body)):
            tax, body = m.groups()  # this is the last thing, so body = ""
            yield "TAX", tax, "X"
        elif (m := re.match(r"(.*?) (\d+\.\d\d)( |-)([A-Z]) (.*)", body)):
            desc, cost, sep, kind, body = m.groups()
            if kind == "B":
                kind = "F"
            else:
                kind = "N"
            if sep == "-":
                cost = sep + cost
            yield desc, cost, kind
        elif (m := re.match(r"(.*) - (\d+\.\d\d) (.*)", body)):
            desc, cost, body = m.groups()
            yield desc, cost, "N"
        else:
            break


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    for i in items:
        print(i.kind, i.desc, i.value)
