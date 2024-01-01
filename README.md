# inbox-spam
Codebase to automatically detect all email content that I should unsubscribe from.

## How to get GMAIL API credentials

Follow the instructions on this page: `https://developers.google.com/gmail/api/quickstart/python`

## How to Run

1. set up your virtual environnment

```
virtualenv -p python3 venv
```

2. install all required libraries

```
pip install -r requirements.txt
```

3. activate your virtual environnment

```
source venv/bin/activate
```

4. run the Jupyter notebook

```
jupyter lab inbox_spam.ipynb
```
