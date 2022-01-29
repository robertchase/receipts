from decimal import Decimal

import pytest

from receipts.item import Item


def test_basic():
    item = Item(Item.FOOD, "Blah", 100.00)
    assert item
    assert item.kind == Item.FOOD
    assert item.desc == "Blah"
    assert isinstance(item.value, Decimal)
    assert item.value == Decimal("100.00")


@pytest.mark.parametrize("kind,desc,value,i_kind,i_desc,i_value", (
    (Item.FOOD, "Blah", "12.34", Item.FOOD, "Blah", Decimal("12.34")),
    (Item.FOOD, "Blah", None, Item.FOOD, "Blah", Decimal("0.00")),
    (Item.NON_FOOD, "Blah", "12.34", Item.NON_FOOD, "Blah", Decimal("12.34")),
    (Item.TAX, "Blah", "12.34", Item.TAX, "Tax", Decimal("12.34")),
    (Item.TAX, None, "12.34", Item.TAX, "Tax", Decimal("12.34")),
    (Item.TOTAL, "Blah", "12.34", Item.TOTAL, "Total", Decimal("12.34")),
    (Item.TOTAL, None, "12.34", Item.TOTAL, "Total", Decimal("12.34")),
    (Item.DATE, "Blah", "2020-12-13", Item.DATE, "Date", "2020-12-13"),
    (Item.DATE, None, "2020-12-13", Item.DATE, "Date", "2020-12-13"),
))
def test_init(kind, desc, value, i_kind, i_desc, i_value):
    item = Item(kind, desc, value)
    assert item.kind == i_kind
    assert item.desc == i_desc
    assert item.value == i_value


def test_bad_date():
    with pytest.raises(ValueError):
        Item(Item.DATE, value="asdf")


def test_bad_number():
    with pytest.raises(ValueError):
        Item(Item.FOOD, "Blah", "asdf")


def test_missing_desc():
    with pytest.raises(ValueError):
        Item(Item.FOOD, value=100)


def invalid_kind():
    with pytest.raises(ValueError):
        Item("Z")
