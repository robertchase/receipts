import pytest

from receipts import safeway


HEADER = (
    "SAFEWAY\n"
    "Store 1234 Dir Foo Barstein\n"
    "Main:(800) 123-4567 RX: (800) 123-4568\n"
    "123 Main Street\n"
    "MYTOWN, MO 12345\n"
    "GROCERY\n"
)


BODY = (
    "JIFFY\n"
    "3.99 B\n"
    "Regular Price 5.49\n"
    "Member Savings 1.50-\n"
    "CHIPS\n"
    "2.49 B\n"
    "Regular Price 2.79\n"
    "Member Savings 0.30-\n"
    "HOT SAUCE\n"
    "3.00 B\n"
    "Regular Price 3.99\n"
    "Member Savings 0.99-\n"
    "COFFEE 11.99 B\n"
    "Regular Price 14.99\n"
    "Member Savings 3.00-\n"
    "STRAWBRRY JUICE 5.79 B\n"
    "GROC NONEDIBLE\n"
    "FOIL\n"
    "5.99 T\n"
    "REFRIG/FROZEN\n"
    "5.97 B\n"
    "3 QTY GREEK YOGURT\n"
    "GEN MERCHANDISE\n"
    "2 QTY TISSUE\n"
    "SWABS\n"
    "10.98 T\n"
    "6.99\n"
    "LIQUOR\n"
    "WINE 10.99 T\n"
    "Age Restricted: 21\n"
    "Regular Price 15.70\n"
    "Member Savings 4.71-\n"
)


FOOTER = (
    "TAX\n"
    "**** BALANCE\n"
    "2.50\n"
    "70.68\n"
    "Credit Purchase 01/08/22 13:46\n"
    "CARD # ***********0123\n"
    "REF: 284644406R66 AUTH: 00826666\n"
    "n\n"
    "PAYMENT AMOUNT\n"
    "70.68\n"
    "AL AMERICAN EXPRESS\n"
    "AID A000000025016666\n"
    "TVR 0000006666\n"
    "TSI E800 11 21\n"
    "OY\n"
    "AMEX\n"
    "70.68\n"
    "CHANGE\n"
    "0.00\n"
    "2.5% SALES TAX\n"
    "1.53\n"
    "3.50% SALES TAX\n"
    "0.59\n"
    "3.50% SALES TAX\n"
    "0.38\n"
    "TOTAL TAX\n"
    "2.50\n"
    "TOTAL NUMBER OF ITEMS SOLD = 13\n"
    "01/08/22 13:46 1689 52 74 8852\n"
    "AW\n"
    "POINTS EARNED TODAY\n"
    "Base Points\n"
    "57\n"
    "112TUD 33\n"
    "TOTAL\n"
    "57\n"
    "Points Towards Next Reward 78 of 100\n"
    "REWARDS AVAILABLE\n"
    "12\n"
    "\n"
)


@pytest.mark.parametrize("data,header,body", (
    (HEADER + BODY, HEADER[:-8], BODY),
    ("ABC\nGROCERY\nDEF", "ABC\n", "DEF"),
    ("ABC\ngarbage GROCERY\nDEF", "ABC\ngarbage ", "DEF"),
    ("ABC\nGROCERY garbage\nDEF", "ABC\n", "DEF"),
))
def test_header(data, header, body):
    a, b = safeway.header(data)
    assert a == header
    assert b == body


@pytest.mark.parametrize("data,body,footer", (
    (BODY + FOOTER, BODY[:-1], FOOTER[4:]),
    ("ABC\nTAX\nDEF", "ABC", "DEF"),
))
def test_footer(data, body, footer):
    a, b = safeway.footer(data)
    assert a == body
    assert b == footer


def test_dollars():
    result = safeway.dollars(FOOTER)
    assert result == [
        "2.50", "70.68", "70.68", "70.68", "0.00", "1.53",
        "0.59", "0.38", "2.50"
    ]


def test_tax():
    result = safeway.tax(FOOTER)
    assert result == "2.50"


def test_total():
    result = safeway.total(FOOTER)
    assert result == "70.68"


def test_date():
    result = safeway.date(FOOTER)
    assert result == "2022-01-08"


def test_clean():
    cleaned = safeway.clean(BODY)
    assert cleaned == [
        "JIFFY", "3.99 B", "CHIPS", "2.49 B", "HOT SAUCE", "3.00 B",
        "COFFEE 11.99 B", "STRAWBRRY JUICE 5.79 B", "FOIL", "5.99 T", "5.97 B",
        "3 QTY GREEK YOGURT", "2 QTY TISSUE", "SWABS", "10.98 T", "6.99",
        "WINE 10.99 T"
    ]


def test_sequence():
    cleaned = safeway.clean(BODY)
    result = safeway.sequence(cleaned)
    result == [
        ("COFFEE", "11.99", "F"), ("STRAWBRRY JUICE", "5.79", "F"),
        ("WINE", "10.99", "N"), ("JIFFY", "3.99", "F"), ("CHIPS", "2.49", "F"),
        ("HOT SAUCE", "3.00", "F"), ("FOIL", "5.99", "N"),
        ("3 QTY GREEK YOGURT", "5.97", "F"), ("2 QTY TISSUE", "10.98", "N"),
        ("SWABS", "6.99", "N")
    ]
