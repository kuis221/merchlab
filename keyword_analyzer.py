from scrapers.keyword_generator import generate_new_searches
from app import db
from collections import Counter

def get_top_10k_shirts(query=None):
	query_sql = ""
	if query:
		query_sql = "and lower(asin_metadata.title) like '%%{}%%'".format(query.lower())


	sql = """
	SELECT asin_metadata.title
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	and asin_analytics.salesrank > 0 and asin_analytics.list_price > 0
	and asin_analytics.salesrank < 10000000
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	{}	
	ORDER BY salesrank ASC 
	LIMIT 10000;
	""".format(query_sql)

	raw_result = db.engine.execute(sql);
	result = [r[0] for r in raw_result]
	return result

def get_trending_tshirts(query=None):
	query_sql = ""
	if query:
		query_sql = "and lower(asin_metadata.title) like '%%{}%%'".format(query.lower())


	sql = """
	SELECT asin_metadata.title
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	
	WHERE salesrank < 1000000 and last_7d_salesrank < 1000000000
	and asin_analytics.list_price > 0
	and asin_analytics.last_7d_salesrank/asin_analytics.salesrank >= 1.2
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	{}
	ORDER BY asin_analytics.last_7d_salesrank/asin_analytics.salesrank DESC 

	LIMIT 10000;
	""".format(query_sql)

	raw_result = db.engine.execute(sql);
	result = [r[0] for r in raw_result]
	return result

def get_counter_and_weights_from_tshirt_titles(titles):
	weights = Counter()
	cnt = Counter()
	for title in titles:
		keywords = generate_new_searches(title)
		for word in keywords:
			# remove bad words
			if len(word) < 3 or len(word.split(" ")) >= 4 or '  ' in word or '   ' in word:
				continue
			cnt[word] += 1
			if len(word.split(" ")) == 2:
				weights[word] += 5
			elif len(word.split(" ")) == 3:
				weights[word] += 10
			else:
				weights[word] += 1
	return cnt, weights

def get_keywords_from_count_data(cnt, highest_weighted_keywords):
	keyword_data = []
	for keyword, weight in highest_weighted_keywords:
		keyword_data.append({"id": keyword, "weight": weight, "count": cnt[keyword]})

	return keyword_data

def get_best_seller_keywords(num_shirts, query=None):
	top_10k_shirts = get_top_10k_shirts(query=query)
	print("num tshirts found345", len(top_10k_shirts))
	cnt, weights = get_counter_and_weights_from_tshirt_titles(top_10k_shirts)
	return get_keywords_from_count_data(cnt, weights.most_common(num_shirts))

def get_trending_tshirt_keywords(num_shirts, query=None):
	trending_tshirts = get_trending_tshirts(query=query)
	print("num tshirts found123", len(trending_tshirts))
	cnt, weights = get_counter_and_weights_from_tshirt_titles(trending_tshirts)
	return get_keywords_from_count_data(cnt, weights.most_common(num_shirts))


def get_keywords_from_titles(num_keywords, titles):
	cnt, weights = get_counter_and_weights_from_tshirt_titles(titles)
	return get_keywords_from_count_data(cnt, weights.most_common(num_keywords))


#get_best_seller_keywords()
#print(get_trending_tshirt_keywords())

if __name__ == '__main__':
	import sys

	if len(sys.argv) == 3:
		analysis_type = sys.argv[1]
		query = sys.argv[2]
	elif len(sys.argv) == 2:
		analysis_type = sys.argv[1]
		query = None

	if analysis_type == "best_sellers":
		print get_best_seller_keywords(100, query)
	elif analysis_type == "trending_tshirts":
		print get_trending_tshirt_keywords(100, query)