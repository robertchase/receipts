# classify grocery receipts
How much do I spend on groceries?

By looking at grocery purchases from credit card statements, I get an
inaccurate number, because grocery stores carry lots of necessary non-food items.
I could make two separate purchases every time I check out (food and non-food), or I could only
buy groceries at the grocery store -- neither option is convenient.

I want to be able to take a picture of my receipt, and have software
separate food from non-food items.

# approach

1. use `google vision` to extract text from a picture of my receipt
2. use `python` to parse the text and give me food and non-food totals

# google vision

The [Google Vision API](https://cloud.google.com/vision) extracts text from images files.
It does lots of other stuff too, but text extraction is the important feature for this project.
The first 1000 calls are free, and after that, the [pricing](https://cloud.google.com/vision/pricing)
is clear and reasonable. If you are scanning more than 1000 grocery receipts a month, then
perhaps you should try making a list.

### feature selection

This project uses the
[Detect text in images](https://cloud.google.com/vision/docs/ocr)
feature of Google Vision, specifically
`DOCUMENT_TEXT_DETECTION`.
This feature is intended for pictures of documents as opposed to pictures which happen to contain some text (like a road sign or whatever).

`DOCUMENT_TEXT_DETECTION` provides all kinds of details
about the text in the image, breaking things down into
pages, blocks, paragraphs, etc. It also provides an overall
chunk of text, which works pretty well for this project.

The accuracy of the text detection seems to be amazing.

### pain points

Receipts tend to look like this:
```
Juice                      1.23
Cereal                     4.56
Corn Chips                 5.67
```

Because of the gap between the description and the price,
the extracted text may not line up -- this could be because
of wrinkles, or the angle of the photograph, or other imperfections.
The resulting data may look like this:
```
Juice
Cereal
1.23
4.56
Corn Chips 5.67
```
Note that things are in order, but they are not always lined up.
Taking care to get a better photograph can improve this alignment problem,
but it isn't always possible to eliminate it.
I'd rather write a smart parser, that is able to deal with these issues,
than waste time re-photographing a receipt until it is perfect (if ever).
The key things to note are:
* the extracted values are very accurate
* the mis-aligned data is presented in a rational order
