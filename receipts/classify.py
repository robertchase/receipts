from decimal import Decimal
import json
import os.path

import click

from receipts import harristeeter
from receipts.item import Item
from receipts import safeway
from receipts import wholefoods


def classify(data, source=None):

    for kind in (harristeeter, safeway, wholefoods):
        if kind.is_receipt(data):
            items = [i for i in kind.classify(data)]
            if source:
                items.append(Item(Item.SOURCE, value=source))
            return items

    raise Exception("unable to classify data")


def json_dump(items):

    base = {
        Item.KIND_NAMES[item.kind]: item.value
        for item in items
        if not isinstance(item.value, Decimal)
    }

    for item in items:
        if item.kind in (Item.FOOD, Item.NON_FOOD):
            serial = item.as_dict()
            serial.update(base)
            print(json.dumps(serial))


@click.command()
@click.argument("source", nargs=-1)
@click.option("--json", "-j", is_flag=True, default=False)
def cli(source, json):

    for path in source:
        with open(path) as filedata:
            data = filedata.read()

        name = os.path.split(path)[1]
        items = classify(data, source=name)
        if json:
            json_dump(items)
        else:
            for item in items:
                print(item)


if __name__ == "__main__":
    cli()
