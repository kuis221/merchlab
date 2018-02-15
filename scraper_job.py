from rq import Queue
from worker import conn
import datetime
from job_util import scrape_merch_asins_task, scrape_from_homepage
from scrapers.scraper_v3 import get_tshirt_products_for_keyword
import firebase_api
from app import db

q = Queue(connection=conn)


def choose_random_keywords(num_keywords):
	sql = """
		SELECT 
			id
		FROM indexed_keyword
		ORDER BY random()
		LIMIT {};
	""".format(str(num_keywords))	
	raw_result = db.engine.execute(sql);
	return [r[0] for r in raw_result]	

def choose_keywords(num_keywords, max_last_indexed_date=None):
	last_indexed_date_sql = ""
	if max_last_indexed_date:
		last_indexed_date_sql = "AND max(indexed_keyword.last_indexed_date) < '{}'".format(max_last_indexed_date)

	sql = """
		SELECT 
			discovery_keyword, count(*), 
			avg(asin_analytics.salesrank) as salesrank_avg, 
			avg(asin_analytics.last_7d_salesrank) as last_7d_salesrank_avg,
			max(indexed_keyword.last_indexed_date) as last_indexed_date
		FROM asin_metadata
		INNER JOIN asin_analytics ON asin_metadata.id=asin_analytics.id
		INNER JOIN indexed_keyword ON asin_metadata.discovery_keyword=indexed_keyword.id
		GROUP BY discovery_keyword
		HAVING 
			avg(asin_analytics.salesrank) < 10000000 
			AND avg(asin_analytics.last_7d_salesrank) < 100000000
			{}
		ORDER BY avg(last_7d_salesrank)/avg(salesrank) DESC
		LIMIT {};
	""".format(last_indexed_date_sql, str(num_keywords))
	print(sql)
	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		result.append({
			"keyword": row[0],
			"number_of_shorts_indexed": row[1],
			"salesrank_avg": row[2],
			"last_7d_salesrank_avg": row[3],
			"last_indexed_date": row[4]
		})
	return result

def create_scraper_job(browse_node, search_index="Apparel", method="random", keywords_to_use=None, num_keywords=200, postfix_variants=["tshirt"]):
	if keywords_to_use and (method or num_keywords):
		print("You cannot specify 'keywords_to_use' argument AND 'num_keywords' argument at the same time. Please specify one or the other.")
		return

	data = {
		"status": "queued",
		"created_at": datetime.datetime.utcnow().isoformat()
	}
	today_str = str(datetime.datetime.today()).split()[0]
	#result = firebase_api.save_object("scrape_merch_asin_task/" + today_str, data)

	#job_id = result["name"]

	if keywords_to_use:
		keywords = keywords_to_use
	else:
		if method == "hot_keywords":
			max_staleness = (datetime.datetime.utcnow() - datetime.timedelta(days=30)).isoformat()
			indexed_keywords = choose_keywords(num_keywords, max_staleness)
			keywords = [k["keyword"] for k in indexed_keywords]
		elif method == "random":
			keywords = choose_random_keywords(num_keywords)

	curr_batch = 0
	batch_size = 50
	while curr_batch*batch_size < len(keywords):
		start = curr_batch*batch_size
		end = (curr_batch+1)*batch_size
		args = (today_str, keywords[start:end], search_index, browse_node, postfix_variants)
		q.enqueue_call(scrape_merch_asins_task, args=args, timeout=7200)		
		curr_batch += 1

	print("created alls craper jobs!")
	#result["datestr"] = today_str
	#return result

#get_tshirt_products_for_keyword("dog")


#further_keywords = scrape_from_homepage(search_index="Kitchen", browse_node="9302388011") # MUG NICHE
#create_scraper_job("9302388011", search_index="Kitchen", method=None, keywords_to_use=further_keywords, num_keywords=None, postfix_variants=["mug"]) # MUG NICHE

create_scraper_job("9302388011", search_index="Kitchen", method="random", num_keywords=60000, postfix_variants=["mug"])

#scrape_from_homepage(search_index="Apparel", browse_node="9056987011")
#scrape_from_homepage(search_index="Apparel", browse_node="9056923011")
#q.enqueue_call(scrape_from_homepage, args=("9056987011",), timeout=7200)
#q.enqueue_call(scrape_from_homepage, args=("9056923011",), timeout=7200)
create_scraper_job("9056987011", search_index="Apparel", method="random", num_keywords=30000, postfix_variants=["tshirt", "longsleeve", "hoodie"])
create_scraper_job("9056923011", search_index="Apparel", method="random", num_keywords=30000, postfix_variants=["tshirt", "longsleeve", "hoodie"])

#create_scraper_job("9056987011", search_index="Apparel", method="hot_keywords", num_keywords=5000, postfix_variants=["tshirt"])
#create_scraper_job("9056923011", search_index="Apparel", method="hot_keywords", num_keywords=5000, postfix_variants=["mug"])


"""
for i in range(50):
	num_keywords=100
	# mens clothing
	result = create_scraper_job("9056987011", num_keywords)

for i in range(50):
	num_keywords=100
	# womens clothing
	result = create_scraper_job("9056923011", num_keywords)
"""