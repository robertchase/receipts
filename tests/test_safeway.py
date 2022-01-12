import pytest

from receipts import safeway


@pytest.mark.parametrize("data,header,body", (
    ("ABC\nGROCERY\nDEF", "ABC\n", "DEF"),
    ("ABC\ngarbage GROCERY\nDEF", "ABC\ngarbage ", "DEF"),
    ("ABC\nGROCERY garbage\nDEF", "ABC\n", "DEF"),
))
def test_header(data, header, body):
    a, b = safeway.header(data)
    assert a == header
    assert b == body


@pytest.mark.parametrize("data,body,footer", (
    ("ABC\nTAX\nDEF", "ABC", "DEF"),
))
def test_footer(data, body, footer):
    a, b = safeway.footer(data)
    assert a == body
    assert b == footer


FOOTER = "\n1.11\n*** BALANCE\n22.22\nFoo 11/22/33 \n3.33\n"


def test_dollars():
    result = safeway.dollars(FOOTER)
    assert result == ["1.11", "22.22", "3.33"]


def test_tax():
    result = safeway.tax(FOOTER)
    assert result == "1.11"


def test_total():
    result = safeway.total(FOOTER)
    assert result == "22.22"


def test_date():
    result = safeway.date(FOOTER)
    assert result == "2033-11-22"


BODY = (
    "FOO 1.23 B\n"
    "Regular Price 1.24\n"
    "Member Savings 0.01-\n"
    "GROC NONEDIBLE\n"
    "LIQUOR\n"
    "TOYS 2.22 T\n"
    "MISCELLANEOUS\n"
)


def test_clean():
    body = safeway.clean(BODY)
    assert body == [
        "FOO 1.23 B",
        "TOYS 2.22 T",
    ]
