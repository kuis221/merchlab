import os

from boto import dynamodb2
from boto.dynamodb2.table import Table
import datetime
import decimal
import boto3
from boto3.dynamodb.conditions import Key
import json

REGION = "us-east-1"
AWS_ACCESS_KEY_ID = 'AKIAJNXO62C54H2EOFUA'
AWS_SECRET_ACCESS_KEY = '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'

client = boto3.client(
    'dynamodb',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    #aws_session_token=SESSION_TOKEN,
    region_name='us-east-1'
)


dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

def write_asin_keywords(keyword, position_mapping):
    TABLE_NAME = "asin_keywords"
    table = dynamodb.Table(TABLE_NAME)

    # Minimum expected keys in keyword_snapshot:
    # 'keyword' key, 'timestamp' key, and 'position_mapping' key
    for position in position_mapping:
        asin = position_mapping[position]
        data = {'asin': asin, 'keyword': keyword, 'position': position}
        response = table.put_item(Item=data)
    return "success"

def write_trademarks_analysis(analysis_snapshot):
    TABLE_NAME = "trademarks_analysis"
    table = dynamodb.Table(TABLE_NAME)

    # Minimum expected keys in analysis_snapshot:
    # 'asin' key, 'timestamp' key, and 'relevant_trademarks' and 'other_trademarks' key
    if 'asin' not in analysis_snapshot or 'timestamp' not in analysis_snapshot:
        return None

    if 'relevant_trademarks' not in analysis_snapshot or 'other_trademarks' not in analysis_snapshot:
        return None

    response = table.put_item(Item=analysis_snapshot)
    return response

def write_keyword_snapshot_to_dynamodb(keyword_snapshot):
    TABLE_NAME = "keyword_snapshot"
    table = dynamodb.Table(TABLE_NAME)

    # Minimum expected keys in keyword_snapshot:
    # 'keyword' key, 'timestamp' key, and 'position_mapping' key
    if 'keyword' not in keyword_snapshot or 'timestamp' not in keyword_snapshot or 'position_mapping'not in keyword_snapshot:
        return None

    response = table.put_item(Item=keyword_snapshot)
    write_asin_keywords(keyword_snapshot["keyword"], json.loads(keyword_snapshot["position_mapping"]))
    return response

def write_snapshot_to_dynamodb(snapshot):
	TABLE_NAME = "asin_snapshot"
	table = dynamodb.Table(TABLE_NAME)

	data = {
		'asin': snapshot.asin,
		'timestamp': datetime.datetime.utcnow().isoformat(),
		'salesrank': snapshot.salesrank,
		'salesrank_category': snapshot.salesrank_category,
		'list_price': snapshot.list_price,
		'currency_code': snapshot.currency_code
	}
	response = table.put_item(Item=data)
	return response


def query_table(table_name, filter_key=None, filter_value=None):
    """
    Perform a query operation on the table. 
    Can specify filter_key (col name) and its value to be filtered.
    """
    table = dynamodb.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.query(KeyConditionExpression=filtering_exp)
    else:
        response = table.query()

    return response

def query_range(table_name, filter_key=None, filter_lb=None, filter_ub=None):
    """
    Perform a query operation on the table. 
    Can specify filter_key (col name) and its value to be filtered.
    """
    table = dynamodb.Table(table_name)

    if filter_key and filter_lb and filter_ub:
        filtering_exp = Key(filter_key).between(filter_lb, filter_ub)
        response = table.query(KeyConditionExpression=filtering_exp)
    else:
        response = table.query()

    return response

def get_snapshots(asin):
	snapshots_json = query_table("asin_snapshot", filter_key='asin', filter_value=asin).get("Items")
	if not snapshots_json:
		return []
	else:
		return snapshots_json

def get_tracked_keywords_for_asin(asin):
    keywords = query_table("asin_keywords", filter_key='asin', filter_value=asin).get("Items")
    if not keywords:
        return []
    else:
        return keywords

def get_trademarks_for_asin(asin):
    trademarks = query_table("trademarks_analysis", filter_key='asin', filter_value=asin).get("Items")
    if not trademarks or len(trademarks) == 0:
        return None
    else:
        return trademarks[0]

