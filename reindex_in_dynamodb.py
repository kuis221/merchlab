import os

from boto import dynamodb2
from boto.dynamodb2.table import Table
import datetime
from scrapers.asin_indexer import get_existing_asins
import models
import decimal
import boto3

TABLE_NAME = "asin_snapshot"
REGION = "us-east-1"
AWS_ACCESS_KEY_ID = 'AKIAJNXO62C54H2EOFUA'
AWS_SECRET_ACCESS_KEY = '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'

"""
conn = dynamodb2.connect_to_region(
    REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
)
table = Table(
    TABLE_NAME,
    connection=conn
)
"""
client = boto3.client(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    #aws_session_token=SESSION_TOKEN,
    region_name='us-east-1'
)


dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

table = dynamodb.Table(TABLE_NAME)



headers = "id,asin,salesrank,salesrank_category,list_price,timestamp,currency_code".split(",")

count = 0
for line in open("asin_snapshot.csv", "r"):
	if count%10 == 0:
		print(count, "progress")
	raw_data = {}
	for i in range(len(headers)):
		header = headers[i]
		value = line.strip().split(',')[i]
		if value != '':
			raw_data[header] = value

	asin = raw_data["asin"]

	timestamp = raw_data.get("timestamp")
	list_price = raw_data.get("list_price")
	if list_price:
		list_price = decimal.Decimal(str(list_price))
			
	salesrank = raw_data.get("salesrank")
	if salesrank:
		salsesrank = int(salesrank)

	data = {
		"asin": asin,
		"timestamp": timestamp,
		"salesrank": salesrank,
		"salesrank_category": raw_data.get("salesrank_category"),
		"list_price": list_price,
		"currency_code": raw_data.get("currency_code"),
	}


	try:
		response = table.put_item(Item=data)

	except Exception as e:
		print(e)
		print(data)
	#print(data)
	count += 1

import json


col_dict = {"datestr": "2017-03-15-def", "asin": "hello", "salesrank": 3000, "salesrank_category": "test"}
response = table.put_item(Item=col_dict)
"""
response = table.update_item(
    Key={
        'asin': "test",
        'timestamp': datetime.datetime.utcnow().isoformat()
    },
    AttributeUpdates={
    	'snapshots': {
    		'Action': "ADD",
    		'Value': {"2017-03-15-def": "abc"}
    	}
    },
    ReturnValues="UPDATED_NEW"
)
"""

