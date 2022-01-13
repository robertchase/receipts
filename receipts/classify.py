from receipts import safeway
from receipts import wholefoods


def classify(data):

    for kind in (safeway, wholefoods):
        if kind.is_receipt(data):
            return kind.classify(data)

    raise Exception("unable to classify data")


if __name__ == "__main__":
    import sys

    with open(sys.argv[1]) as source:
        data = source.read()

    items = classify(data)
    for item in items:
        print(item.kind, item.desc, item.value)
