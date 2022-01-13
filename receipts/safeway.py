from decimal import Decimal
import re

from receipts.item import Item


def is_receipt(data: str) -> bool:
    if re.search("SAFEWAY", data):
        return True
    return False


def classify(data: str) -> list[Item]:
    """parse Items from safeway receipt data"""

    # remove header
    _, data = header(data)

    # isolate body
    body, remainder = footer(data)

    # extract items from body
    normal = sequence(clean(body))
    result = [
        Item(kind, desc, Decimal(cost))
        for desc, cost, kind in normal]

    # extract tax, total and date from footer
    result.append(Item("X", "Tax", Decimal(tax(remainder))))
    result.append(Item("T", "Total", Decimal(total(remainder))))
    result.append(Item("D", "Date", date(remainder)))

    return result


def header(data: str) -> tuple[str, str]:
    """chop the header information off the receipt"""
    return re.split(r"GROCERY.*?\n", data, flags=re.DOTALL)


def footer(data: str) -> tuple[str, str]:
    """chop the footer information off the receipt"""
    return data.split("\nTAX\n")


def dollars(data: str) -> list[str]:
    """extract all dollar.cents lines from data"""
    result = []
    for line in data.split("\n"):
        if re.match(r"\d+\.\d\d$", line):
            result.append(line)
    return result


def tax(data: str) -> str:
    """extract tax (first dollar value) from footer"""
    return dollars(data)[0]


def total(data: str) -> str:
    """extract total (second dollar value) from footer"""
    return dollars(data)[1]


def date(data: str) -> str:
    """extract transaction date from footer"""
    if (s := re.search(r"(\d\d)/(\d\d)/(\d\d) ", data)):
        month, day, year = s.groups()
        return f"20{year}-{month}-{day}"


def clean(data: str) -> list[str]:
    """remove unused lines"""
    remove = [
        "Regular Price",
        "Member Savings",
        "Age Restricted",
        "GEN MERCHANDISE",
        "GROC NONEDIBLE",
        "LIQUOR",
        "PRODUCE",
        "REFRIG/FROZEN",
        "MISCELLANEOUS",
    ]

    def keep(data):
        for check in remove:
            if data.find(check) >= 0:
                return False
        return True

    result = []
    for line in data.split("\n"):
        if len(line.strip()):
            if keep(line):
                result.append(line)
    return result


def sequence(data: list[str]) -> list[tuple[str, str, str]]:
    """rearrange lines to match up description and cost

       things can end up misaligned in the ocr output with multiple
       descriptions or multiple costs grouped together -- this logic tries to
       remedy the non-lined-up items by grouping orphaned descriptions and
       costs and matching them up

       return list of (desc, cost, kind)
    """

    def normalize_kind(kind: str) -> str:
        if kind == "B":  # indicates a food item
            return "F"
        return "N"  # otherwise, non-food

    result = []
    costs = []
    descriptions = []
    for line in data:

        # full match
        if (m := re.match(r"(.*?) (\d+\.\d\d) ([A-Z])", line)):
            desc, cost, kind = m.groups()
            kind = normalize_kind(kind)
            result.append((desc, cost, kind))

        # cost and kind
        elif (m := re.match(r"(\d+\.\d\d) ([A-Z])", line)):
            cost, kind = m.groups()
            kind = normalize_kind(kind)
            costs.append((cost, kind))

        # cost
        elif re.match(r"\d+\.\d\d", line):
            costs.append((line, normalize_kind("")))  # non-food

        # description (everything else)
        else:
            descriptions.append(line)

    for desc, cost in zip(descriptions, costs):
        cost, kind = cost
        result.append((desc, cost, kind))

    return result


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    for i in items:
        print(i.kind, i.desc, i.value)
