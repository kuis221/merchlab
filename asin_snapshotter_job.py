from job_util import snapshot_asins
from scrapers.asin_indexer import get_existing_asins
from rq import Queue
from worker import conn
from models import AsinAnalytics
from app import db
q = Queue(connection=conn)

def enqueue_in_batches(asins, batch_size=1000):
	i = 0
	while i < len(asins):
		curr_asins = asins[i:i+batch_size]
		args = (curr_asins, )
		q.enqueue_call(snapshot_asins, args=args, timeout=3600)
		i += batch_size

def snapshot_asins_missing_data(max_num_asins=None):
	asins = list(get_existing_asins())
	asins_to_enqueue = []
	for asin in asins:
		analytics = AsinAnalytics.query.filter_by(id=asin).first()
		if not analytics or not analytics.salesrank or not analytics.list_price:
			asins_to_enqueue.append(asin)

		if max_num_asins and len(asins_to_enqueue) == max_num_asins:
			break

	enqueue_in_batches(asins_to_enqueue)


def snapshot_asins_between_salesrank_range(min_salesrank=0, max_salesrank=3000000, max_num_asins=1000000, use_unthrottled_salesrank=False):
	
	column_name = "salesrank"
	if use_unthrottled_salesrank:
		column_name = "unthrottled_salesrank"

	sql = """
	SELECT asin_metadata.id FROM asin_metadata 
	JOIN asin_analytics ON asin_metadata.id=asin_analytics.id 
	WHERE asin_analytics.{} > {} and asin_analytics.{} < {}
	AND asin_metadata.product_type_name='ORCA_SHIRT'
	ORDER BY asin_analytics.{} ASC
	LIMIT {};
	""".format(column_name, min_salesrank, column_name, max_salesrank, column_name, max_num_asins)

	raw_result = db.engine.execute(sql);
	asins = []
	for row in raw_result:
		asins.append(row[0])

	enqueue_in_batches(asins)


snapshot_asins_between_salesrank_range(min_salesrank=0, max_salesrank=20000000, use_unthrottled_salesrank=False)
snapshot_asins_between_salesrank_range(min_salesrank=0, max_salesrank=20000000, use_unthrottled_salesrank=True)



