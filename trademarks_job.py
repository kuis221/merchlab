from app import db
from rq import Queue
from worker import conn
import datetime
from datetime import timedelta
from job_util import scrape_trademarks_analysis_for_asins

q = Queue(connection=conn)

def get_asins_with_stale_trademark_info():
	asins = []
	# Grab asins where last trademark scraper job was triggered 30 days ago
	min_staleness = datetime.datetime.now() - timedelta(days=30)

	sql = """
	SELECT asin_metadata.id
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	and asin_analytics.salesrank > 0
	and asin_analytics.salesrank < 500000
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	and COALESCE(asin_analytics.last_trademark_indexed_date, '') < '{}'
	ORDER BY salesrank ASC 
	LIMIT 100000;
	""".format(min_staleness)

	raw_result = db.engine.execute(sql);

	for result in raw_result:
		asin = result[0]
		asins.append(asin)

	return asins



asins = get_asins_with_stale_trademark_info()

curr_page = 0
batch_size = 30

while curr_page*batch_size < len(asins):
	start = curr_page * batch_size
	end = (curr_page+1) * batch_size
	curr_asins = asins[start:end]
	q.enqueue_call(scrape_trademarks_analysis_for_asins, args=(curr_asins,))
	curr_page += 1

