# classify grocery receipts
How much do I spend on groceries?

By only looking at grocery purchases from credit card statements, I get an
inaccurate number, because grocery stores carry lots of necessary non-food items.
I could make two separate purchases every time I check out, or I could only
buy groceries at the grocery store -- neither option is convenient.

I want to be able to take a picture of my receipt, and have software
separate food from non-food items.

# approach

1. use `google vision` to extract text from a picture of my receipt
2. use `python` to parse the text and give me food and non-food totals
