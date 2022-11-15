# canaal-tron

## Starting Twitter Sentiment Analysis Data Stream
- Navigate to canaal-aws
- Make sure you create a file keys.py containing your AWS and Twitter API keys (contact me if need temporary keys)
- Run **1.lambda-api.ipynb** except the last cell
- Run **Twitter-Listener.ipynb**

## Creating application for real-time continuous SQL queries
- Navigate to canaal-aws
- Run **2.kinesis-data-streams** except the last cell

## Accessing frontend
- Navigate to canaal-flask
- Run command **python app.py**

## Changing authorized addresses through Merkle Proof
- Navigate to canaal-merkle
- Change addresses in **addresses.json**
- Follow instructions on this link https://github.com/ItsCuzzo/merkleAPI on how to update the authentification unit.
- Change the merkle API URL in canaal-flask/app.py to the new merkle API URL
