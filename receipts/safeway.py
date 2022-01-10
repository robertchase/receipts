from decimal import Decimal
import re

from receipts.item import Item


def is_receipt(data):
    if re.search("SAFEWAY", data):
        return True
    return False


def classify(data):
    """parse Items from safeway receipt data"""
    result = []

    # remove header
    data = re.split(r"GROCERY", data, flags=re.DOTALL)[1]

    # remove newlines
    data = data.replace("\n", " ")

    # for each purchase
    while (s := re.search("(^.*?) (\d+\.\d\d) (B|T) (.*)", data)):
        desc, cost, kind, data = s.groups()
        if kind == "B":
            kind = "F"
        else:
            kind = "N"

        result.append(Item(kind, desc, Decimal(cost)))

        # after wine
        if (s := re.match("Age Restricted:\s+\S+ (.*)", data)):
            data, = s.groups()

        # member discount
        if (s := re.match("Regular Price\s+\S+ (.*)", data)):
            data, = s.groups()
        if (s := re.match("Member Savings\s+\S+ (.*)", data)):
            data, = s.groups()

        # charge for bags
        if (s := re.match("(MISCELLANEOUS .+?)(\d+\.\d\d) (.*)", data)):
            misc, cost, data = s.groups()
            result.append(Item("N", misc, Decimal(cost)))

    # tax
    if (s := re.match("TAX .*?(\d+\.\d\d) (.*)", data)):
        cost, data = s.groups()
        result.append(Item("X", "Tax", Decimal(cost)))

    # total charged
    if (s := re.search("BALANCE\s+(\d+\.\d\d) (.*)", data)):
        cost, data = s.groups()
        result.append(Item("T", "Total", Decimal(cost)))

    # date of transacdtion
    if (s := re.search("(\d\d)/(\d\d)/(\d\d) (.*)", data)):
        month, day, year, data = s.groups()
        result.append(Item("D", "Date", f"20{year}-{month}-{day}"))

    # remaining data
    result.append(Item("R", data, 0))
    return result


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    for i in items:
        print(i.type, i.desc, i.amount)
