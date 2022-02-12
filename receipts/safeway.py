import re

import click

from receipts.item import Item


NAME = "SAFEWAY"


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
    items, costs = categorize(trimmed_body)
    # collate orphan costs with incomplete lines
    collated = collate(items, costs)
    # remove discount lines
    result = remove_discount(collated)
    result.append(Item(Item.VENDOR, value=NAME))

    # extract tax, total and date from footer
    result.append(Item(Item.TAX, value=tax(remainder)))
    result.append(Item(Item.TOTAL, value=total(remainder)))
    result.append(Item(Item.DATE, value=date(remainder)))

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
        "1 QTY",
        "Age Restricted: 21",
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


class Description(Item):
    def __init__(self, description):
        super().__init__(self.DESCRIPTION, desc=description)

    DESCRIPTION = "."
    VALID_KIND = Item.VALID_KIND + (DESCRIPTION,)


class Cost(Item):
    def __init__(self, kind, cost):
        super().__init__(kind, desc="Cost", value=cost)

    @property
    def cost(self):
        return self.value


def categorize(data: list[str]) -> tuple[list[Item], list[Cost]]:
    """categorize data into descriptions and costs

       things can end up misaligned in the ocr output with multiple
       descriptions or multiple costs grouped together -- this tries to fix
       this by isolating orphaned descriptions and costs
    """
    items = []
    costs = []
    for line in data:

        # full match
        if (m := re.match(r"(.*?) (\d+\.\d\d) (B|T)", line)):
            desc, cost, kind = m.groups()
            kind = Item.FOOD if kind == "B" else Item.NON_FOOD
            items.append(Item(kind, desc, cost))

        # "Regular Price" or "Member Savings" and cost
        elif (m := re.match(
                r"((?:Regular Price)|(?:Member Savings)) (\d+\.\d\d)-?",
                line)):
            desc, cost = m.groups()
            items.append(Item(Item.NON_FOOD, desc, cost))

        # desc and cost
        elif (m := re.match(r"(.*?) (\d+\.\d\d)", line)):
            desc, cost = m.groups()
            items.append(Item(Item.NON_FOOD, desc, cost))

        # cost and kind
        elif (m := re.match(r"(\d+\.\d\d) (B|T)", line)):
            cost, kind = m.groups()
            kind = Item.FOOD if kind == "B" else Item.NON_FOOD
            costs.append(Cost(kind, cost))

        # cost
        elif (m := re.match(r"(\d+\.\d\d)(-?)", line)):
            cost, sign = m.groups()
            costs.append(Cost(Item.NON_FOOD, sign + cost))

        # description (everything else)
        else:
            items.append(Description(line))

    return items, costs


def collate(items, costs):
    """re-unite orphaned descriptions and costs"""

    for item in items:
        if item.kind == Description.DESCRIPTION:
            if not len(costs):
                raise Exception(f"no matching cost for {item.desc}")
            cost, costs = costs[0], costs[1:]
            item.kind = cost.kind
            item.value = cost.cost

    return items


def remove_discount(items):
    return [item for item in items
            if item.desc not in ("Regular Price", "Member Savings")]


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


@cli.command("categorize")
@click.argument("input", type=click.File("r"))
def _categorize(input):
    """display categorized items from receipt"""
    data = input.read()
    _, data = header(data)
    body, _ = footer(data)
    items, _ = categorize(remove_labels(body))
    for item in items:
        print(item)


@cli.command()
@click.argument("input", type=click.File("r"))
def costs(input):
    """display cost from receipt"""
    data = input.read()
    _, data = header(data)
    body, _ = footer(data)
    _, costs = categorize(remove_labels(body))
    for item in costs:
        print(item)


@cli.command("collate")
@click.argument("input", type=click.File("r"))
def _collate(input):
    """display collated items from receipt"""
    data = input.read()
    _, data = header(data)
    body, _ = footer(data)
    trimmed_body = remove_labels(body)
    items, costs = categorize(trimmed_body)
    collated = collate(items, costs)

    for item in collated:
        print(item)


@cli.command()
@click.argument("input", type=click.File("r"))
def sidebyside(input):
    """display collated items side by side"""
    data = input.read()
    _, data = header(data)
    body, _ = footer(data)
    trimmed_body = remove_labels(body)
    items, costs = categorize(trimmed_body)

    for item in items:
        if item.kind == Description.DESCRIPTION:
            if len(costs):
                cost, costs = costs[0], costs[1:]
            else:
                cost = None
            print(item.kind, item.desc, cost.cost if cost else "*")
        else:
            print(item)


if __name__ == "__main__":
    cli()
