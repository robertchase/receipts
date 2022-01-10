from google.cloud import vision


def annotate(image_file_name):
    """call google vision to extract text from image"""
    with open(image_file_name, "rb") as data:
        content = data.read()
    image = vision.Image(content=content)
    client = vision.ImageAnnotatorClient()
    return client.document_text_detection(image=image)


if __name__ == "__main__":
    import sys

    image_file = sys.argv[1]
    text = annotate(image_file)
    print(text.text_annotations[0].description)
