import json
import os.path

import click

from receipts import harristeeter
from receipts.item import Item
from receipts import safeway
from receipts import wholefoods


def classify(data):

    for kind in (harristeeter, safeway, wholefoods):
        if kind.is_receipt(data):
            return kind.classify(data)

    raise Exception("unable to classify data")


def json_dump(items, source_item):

    date = vendor = None
    for item in items:
        if item.kind == Item.DATE:
            date = item.value
        elif item.kind == Item.VENDOR:
            vendor = item.value

    for item in items:
        if item.kind in (Item.FOOD, Item.NON_FOOD):
            ditem = item.as_dict()
            ditem["date"] = date
            ditem["vendor"] = vendor
            ditem["source"] = source_item.value
            print(json.dumps(ditem))


@click.command()
@click.argument("source", type=click.File())
@click.option("--json", "-j", is_flag=True, default=False)
def cli(source, json):

    data = source.read()
    source_item = Item(Item.SOURCE, value=os.path.split(source.name)[1])

    items = classify(data)
    if json:
        json_dump(items, source_item)
    else:
        for item in items:
            print(item)
        print(source_item)


if __name__ == "__main__":
    cli()
