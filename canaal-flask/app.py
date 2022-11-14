import os
from flask import Flask, render_template, abort, url_for, request, jsonify

import json
import requests

import boto3
import keys
import os

os.environ['AWS_ACCESS_KEY_ID'] = keys.AWS_ACCESS_KEY_ID
os.environ['AWS_SECRET_ACCESS_KEY'] = keys.AWS_SECRET_ACCESS_KEY
os.environ['AWS_DEFAULT_REGION'] = keys.AWS_DEFAULT_REGION
kinesis_client = boto3.client('kinesis')

shard_iterator = kinesis_client.get_shard_iterator(StreamName='canaal-output', 
                                                   ShardId='shardId-000000000000',
                                                   ShardIteratorType='LATEST')

app = Flask(__name__)

@app.route('/', methods=['GET','POST'])
def index():
    if request.method == "POST":
        address = request.form['address']
        if address:
            merkle = requests.get(f'https://xf6u3cmhe7.execute-api.us-east-2.amazonaws.com/proof/{address}')
            if merkle.text != '[]':
                while True:
                    data = kinesis_client.get_records(ShardIterator=shard_iterator['ShardIterator'])
                    if data['Records'] != []:
                        payload = [json.dumps(eval(i['Data'])) for i in kinesis_client.get_records(ShardIterator=shard_iterator['ShardIterator'])['Records']]
                        return json.dumps(payload)
            else:
                return json.dumps({'hi':'Unauthorized Account'})
        else:
            return json.dumps({'hi':'MetaMask not Connected'})
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)