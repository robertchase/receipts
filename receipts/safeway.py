from decimal import Decimal
import re

import click

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

    # remove section labels
    trimmed_body = remove_labels(body)
    # separate data into full/partial items and orphaned costs
    lines, costs = categorize(trimmed_body)
    # collate orphan costs with incomplete lines
    collated = collate(lines, costs)
    # remove discount lines
    normal = remove_discount(collated)

    # turn normalized data into Items
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


def remove_labels(data: str) -> list[str]:
    """remove unused lines"""
    remove = [
        "Age Restricted",
        "DELI",
        "FLORAL",
        "GEN MERCHANDISE",
        "GROC NONEDIBLE",
        "LIQUOR",
        "PRODUCE",
        "REFRIG/FROZEN",
        "MISCELLANEOUS",
        "MR",  # sometimes this "breaks off" from the "DSPSBL BAG" line
    ]

    def keep(data):
        for check in remove:
            if data == check:
                return False
        return True

    result = []
    for line in data.split("\n"):
        if len(line.strip()):
            if keep(line):
                result.append(line)
    return result


def categorize(data: list[str]) -> tuple[list[str], list[str]]:
    """categorize data into descriptions and costs

       things can end up misaligned in the ocr output with multiple
       descriptions or multiple costs grouped together -- this tries to fix
       this by isolating orphaned descriptions and costs
    """
    lines = []  # list[[desc, cost, kind]]
    costs = []  # list[[cost, kind]]
    for line in data:

        # full match
        if (m := re.match(r"(.*?) (\d+\.\d\d) (B|T)", line)):
            desc, cost, kind = m.groups()
            kind = "F" if kind == "B" else "N"
            lines.append([desc, cost, kind])

        # "Regular Price" or "Member Savings" and cost
        elif (m := re.match(
                r"((?:Regular Price)|(?:Member Savings)) (\d+\.\d\d-?)",
                line)):
            desc, cost = m.groups()
            lines.append([desc, cost, "N"])

        # desc and cost
        elif (m := re.match(r"(.*?) (\d+\.\d\d)", line)):
            desc, cost = m.groups()
            lines.append([desc, cost, "N"])

        # cost and kind
        elif (m := re.match(r"(\d+\.\d\d) (B|T)", line)):
            cost, kind = m.groups()
            kind = "F" if kind == "B" else "N"
            costs.append((cost, kind))

        # cost
        elif (m := re.match(r"(\d+\.\d\d-?)", line)):
            cost = m.group(1)
            costs.append((cost, "N"))

        # description (everything else)
        else:
            lines.append([line, 0, "N"])

    return lines, costs


def collate(lines, costs):
    """re-unite orphaned descriptions and costs"""

    for line in lines:
        desc, cost, kind = line
        if cost == 0:  # every time cost is zero, fill in from "costs"
            next_cost, costs = costs[0], costs[1:]
            line[1], line[2] = next_cost

    return lines


def remove_discount(data: list[tuple[str, str, str]]) -> list[
        tuple[str, str, str]]:
    return [item for item in data
            if item[0] not in ("Regular Price", "Member Savings")]


@click.group()
def cli():
    pass


@cli.command()
@click.argument("input", type=click.File("r"))
def parse(input):
    """display parsed data from receipt"""
    data = input.read()
    items = classify(data)
    for i in items:
        print(i.kind, i.desc, i.value)


@cli.command()
@click.argument("input", type=click.File("r"))
def desc(input):
    """display descriptions from receipt"""
    data = input.read()
    _, data = header(data)
    body, _ = footer(data)
    lines, _ = categorize(remove_labels(body))
    lines = remove_discount(lines)
    for line in lines:
        print(line[0])


if __name__ == "__main__":
    cli()
