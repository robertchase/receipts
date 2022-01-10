# tutorial
https://codelabs.developers.google.com/codelabs/cloud-vision-api-python

# setup python
Note: requires at least 3.8 in order to support the `walrus`.
```
brew install python3 # or however you get access to a recent version
python3 -m venv env
. ./env/bin/activate
pip install -U pip google-cloud-vision
```

# virtual env
`. ./env/bin/activate`

# cloud vision creds
`export GOOGLE_APPLICATION_CREDENTIALS=<location of cred file>`

# extract text
`python -m receipts.vision image_file_name > receipt.txt`
