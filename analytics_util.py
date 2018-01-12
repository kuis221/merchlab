import models
from app import db
from sqlalchemy import desc
import statistics
from dateutil import relativedelta
import datetime
from scrapers.asin_indexer import get_existing_asins
import boto3
from boto3.dynamodb.conditions import Key
from rq import Queue
from worker import conn

q = Queue(connection=conn)

TABLE_NAME = "asin_snapshot"
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


#items = query_table(TABLE_NAME, filter_key='asin', filter_value='B0713XDV9D').get("Items")
#items = query_table(TABLE_NAME, filter_key=None, filter_value=None).get("Items")
#print(items)


def compute_analytics_data_for_asins(asins):
	#asins = list(get_existing_asins())
	#asins = asins[curr_page*batch_size:(curr_page+1)*batch_size]


	today = datetime.datetime.utcnow()

	for i, asin in enumerate(asins):
		curr_snapshots_json = query_table("asin_snapshot", filter_key='asin', filter_value=asin).get("Items")
		curr_snapshots = [models.AsinSnapshot(data) for data in curr_snapshots_json]

		newest_snapshot = get_newest_snapshot(curr_snapshots)
		newest_unthrottled_snapshot = get_newest_unthrottled_snapshot(curr_snapshots)

		if not newest_snapshot:
			newest_salesrank = None
			newest_list_price = None
		else:
			newest_salesrank = newest_snapshot.salesrank
			newest_list_price = newest_snapshot.list_price

		if not newest_unthrottled_snapshot:
			newest_unthrottled_salesrank = None
		else:
			newest_unthrottled_salesrank = newest_unthrottled_snapshot.salesrank

		#print("got newest salesrank", newest_salesrank, newest_list_price)
		#curr_snapshots = models.AsinSnapshot.query.filter_by(asin=asin).all()
		seven_days_ago = today - relativedelta.relativedelta(days=7)
		filtered_snapshots = filter_snapshots_within_range(curr_snapshots, seven_days_ago.isoformat(), today.isoformat())
		seven_days_avg_salesrank = compute_average_salesrank_for_asin(filtered_snapshots)
		#print("got seven days avg salesrank")

		one_month_ago = today - relativedelta.relativedelta(months=1)
		filtered_snapshots = filter_snapshots_within_range(curr_snapshots, one_month_ago.isoformat(), today.isoformat())
		one_month_avg_salesrank = compute_average_salesrank_for_asin(filtered_snapshots)
		#print("got one avg salesrank")

		three_months_ago = today - relativedelta.relativedelta(months=3)
		filtered_snapshots = filter_snapshots_within_range(curr_snapshots, three_months_ago.isoformat(), today.isoformat())
		three_months_avg_salesrank = compute_average_salesrank_for_asin(filtered_snapshots)
		#print("got three month savg")

		escore = compute_escore(filtered_snapshots)
		weighted_escore_v1 = compute_weighted_escore_v1(filtered_snapshots)
		weighted_escore_v2 = compute_weighted_escore_v2(filtered_snapshots)
		weighted_escore_v3 = compute_weighted_escore_v3(filtered_snapshots)
		streak_score_v1 = compute_streak_score_v1(filtered_snapshots)
		streak_score_v2 = compute_streak_score_v2(filtered_snapshots)

		data = {
			"last_indexed_date": datetime.datetime.utcnow(),
			"asin": asin,
			"salesrank": newest_salesrank,
			"unthrottled_salesrank": newest_unthrottled_salesrank,
			"list_price": newest_list_price,
			"last_7d_salesrank": seven_days_avg_salesrank,
			"last_1mo_salesrank": one_month_avg_salesrank,
			"last_3mo_salesrank": three_months_avg_salesrank,
			"escore": escore,
			"weighted_escore_v1": weighted_escore_v1,
			"weighted_escore_v2": weighted_escore_v2,
			"weighted_escore_v3": weighted_escore_v3,
			"streak_score_v1": streak_score_v1,
			"streak_score_v2": streak_score_v2,

			#"last_7d_list_price": last_7d_list_price,
			#"last_1mo_list_price": last_1m_list_price,
			#"last_3mo_list_price": last_3m_list_price,
			#"last_7d_volatility": last_7d_volatility,
			#"last_1mo_volatility": last_1m_volatility,
			#"last_3mo_volatility": last_3m_volatility,
		}

		print("this is the data we snapshotted", data)

		asin_analytics_entry = models.AsinAnalytics.query.filter_by(id=asin).first()
		if not asin_analytics_entry:
			asin_analytics_entry = models.AsinAnalytics(data)
			db.session.add(asin_analytics_entry)
		else:
			asin_analytics_entry.update_item(data)


		new_data = {
			"asin_salesrank": newest_salesrank,
			"asin_unthrottled_salesrank": newest_unthrottled_salesrank,
			"asin_list_price": newest_list_price
		}
		models.AsinMetadata.query.filter_by(id=asin).update(new_data)

		try:
			db.session.commit()
			print("success")
		except Exception as e:
			print("it rolled back")
			db.session.rollback()
			print(e)

def get_newest_snapshot(snapshots):
	latest_ts = None
	newest_snapshot = None
	for snapshot in snapshots:
		if not latest_ts:
			newest_snapshot = snapshot
			latest_ts = newest_snapshot.timestamp
		elif snapshot.timestamp > latest_ts:
			newest_snapshot = snapshot
			latest_ts = newest_snapshot.timestamp

	return newest_snapshot


def get_newest_unthrottled_snapshot(snapshots):
	latest_ts = None
	newest_snapshot = None
	for snapshot in snapshots:
		if not latest_ts:
			if snapshot.salesrank > 0:
				newest_snapshot = snapshot
				latest_ts = newest_snapshot.timestamp

		elif snapshot.timestamp > latest_ts and snapshot.salesrank > 0:
			newest_snapshot = snapshot
			latest_ts = newest_snapshot.timestamp

	return newest_snapshot




def filter_snapshots_by_asin(snapshots, asin):
	filtered = []
	for snapshot in snapshots:
		if snapshot.asin == asin:
			filtered.append(snapshot)
	return filtered

def get_newest_salesrank(asin):
	latest_snapshot = models.AsinSnapshot.query.filter_by(asin=asin).order_by(desc(models.AsinSnapshot.timestamp)).first()
	if latest_snapshot:
		return latest_snapshot.salesrank
	return None

def compute_average_salesrank_for_asin(snapshots):
	values = []
	for snapshot in snapshots:
		salesrank = snapshot.salesrank
		try:
			salesrank = int(salesrank)
		except Exception as e:
			continue
		values.append(salesrank)
	if len(values) == 0:
		return None

	return statistics.mean(values)

def compute_escore(snapshots):
	print("input", len(snapshots))
	sorted_snapshots = sorted(snapshots, key=lambda k: k.timestamp)
	score = 0
	i = 0
	while i < len(sorted_snapshots)-1:
		curr_snap = sorted_snapshots[i]
		next_snap = sorted_snapshots[i+1]
		if next_snap.salesrank <= curr_snap.salesrank:
			score += 1
		i += 1
	return score

def compute_weighted_escore_v1(snapshots):
	sorted_snapshots = sorted(snapshots, key=lambda k: k.timestamp)
	score = 0
	i = 0
	while i < len(sorted_snapshots)-1:
		curr_snap = sorted_snapshots[i]
		next_snap = sorted_snapshots[i+1]
		if next_snap.salesrank < curr_snap.salesrank:
			score += 5
		if next_snap.salesrank == curr_snap.salesrank:
			score += 1
		i += 1
	return score

def compute_weighted_escore_v2(snapshots):
	sorted_snapshots = sorted(snapshots, key=lambda k: k.timestamp)
	score = 0
	i = 0
	while i < len(sorted_snapshots)-1:
		curr_snap = sorted_snapshots[i]
		next_snap = sorted_snapshots[i+1]
		if next_snap.salesrank < curr_snap.salesrank:
			score += 2
		if next_snap.salesrank == curr_snap.salesrank:
			score += 1
		i += 1
	return score

def compute_weighted_escore_v3(snapshots):
	sorted_snapshots = sorted(snapshots, key=lambda k: k.timestamp)
	score = 0
	i = 0
	while i < len(sorted_snapshots)-1:
		curr_snap = sorted_snapshots[i]
		next_snap = sorted_snapshots[i+1]
		if next_snap.salesrank < curr_snap.salesrank:
			score += 2
		if next_snap.salesrank == curr_snap.salesrank:
			score += 1
		if next_snap.salesrank > curr_snap.salesrank:
			score - 5
		i += 1
	return score

def compute_streak_score_v1(snapshots):
	# Sum of squared streak lengths

	sorted_snapshots = sorted(snapshots, key=lambda k: k.timestamp)
	score = 0
	i = 0
	curr_streak = 0
	while i < len(sorted_snapshots)-1:
		curr_snap = sorted_snapshots[i]
		next_snap = sorted_snapshots[i+1]
		if next_snap.salesrank < curr_snap.salesrank:
			curr_streak += 1
		elif next_snap.salesrank == curr_snap.salesrank:
			curr_streak += 1
		else:
			score += curr_streak * curr_streak
			curr_streak = 0
		i += 1
	return score

def compute_streak_score_v2(snapshots):
	# Sum of squared streak lengths

	sorted_snapshots = sorted(snapshots, key=lambda k: k.timestamp)
	score = 0
	i = 0
	curr_streak = 0
	while i < len(sorted_snapshots)-1:
		curr_snap = sorted_snapshots[i]
		next_snap = sorted_snapshots[i+1]
		if next_snap.salesrank < curr_snap.salesrank:
			curr_streak += 5
		elif next_snap.salesrank == curr_snap.salesrank:
			curr_streak += 2
		else:
			score += curr_streak * curr_streak
			curr_streak = 0
		i += 1
	return score	

def filter_snapshots_within_range(snapshots, start_str, end_str):
	filtered = []
	for snapshot in snapshots:
		if snapshot.timestamp < start_str or snapshot.timestamp > end_str:
			continue
		filtered.append(snapshot)
	return filtered

def compute_avg_asin_volatility_data():
	pass

