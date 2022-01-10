from decimal import Decimal
import re

from receipts.item import Item


def is_receipt(data):
    if re.search("WH.LE FOODS", data):
        return True
    return False


def classify(data):
    """parse Items from wholefoods receipt data"""
    result = []

    # remove header
    data = re.split(r"WH.LE FOODS.*?MARKET\n.+?, [A-Z]{2} \d{5}.*?\n",
                    data, flags=re.DOTALL)[1]

    # remove newlines
    data = data.replace("\n", " ")

    # for each purchase
    while (s := re.search("(^.*?) \$(\d+\.\d\d) (F?T) (.*)", data)):
        desc, cost, kind, data = s.groups()

        if desc.find("HOT BAR") >= 0:  # treat HOT BAR like food
            kind = "F"
        elif kind == "FT":
            kind = "F"
        else:
            kind = "N"

        result.append(Item(kind, desc, Decimal(cost)))

        if (s := re.match("(\*Sale\*.+?)- ?\$(\d+\.\d\d) (.*)", data)):
            desc, discount, data = s.groups()
            result.append(Item(kind, desc, -Decimal(discount)))
            
        if (s := re.match("(Prime Extra.+?)- ?\$(\d+\.\d\d) (.*)", data)):
            desc, discount, data = s.groups()
            result.append(Item(kind, desc, -Decimal(discount)))
            
    while (s := re.search("(Tax:? \d\.\d\d%) \$(\d\.\d\d) (.*)", data)):
        desc, cost, data = s.groups()
        result.append(Item("X", "Tax", Decimal(cost)))
            
    if (s := re.search("Total: +?\$(\d+\.\d\d) (.*)", data)):
        cost, data = s.groups()
        result.append(Item("T", "Total", Decimal(cost)))
            
    if (s := re.search("(\d\d)/(\d\d)/(20\d\d) (.*)", data)):
        month, day, year, data = s.groups()
        result.append(Item("D", "Date", f"{year}-{month}-{day}"))

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
