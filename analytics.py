from scrapers.asin_indexer import get_existing_asins
from analytics_util import compute_analytics_data_for_asins
from rq import Queue
from worker import conn
from app import db
from models import AsinMetadata

q = Queue(connection=conn)


def compute_analytics_data():
	
	query = AsinMetadata.query
	window_size = 1000
	window_idx = 0
	while True:
		print("hello")
		start,stop = window_size*window_idx, window_size*(window_idx+1)
		items = query.slice(start, stop).all()
		asins = [item.id for item in items]
		print(asins)
		if items is None:
			break
		
		args = (asins, )
		q.enqueue_call(compute_analytics_data_for_asins, args=args, timeout=720)
	  
		if len(asins) < window_size:
			break
		window_idx += 1

	"""
	batch_size = 10000
	curr_page = 0
	asins = list(get_existing_asins())

	#while curr_page < 2:
	while curr_page*batch_size <= len(list(asins)):
		print(float(curr_page*batch_size) / float(len(asins)))
		args = (curr_page, batch_size)	
		q.enqueue_call(compute_analytics_data_for_asins, args=args, timeout=720)

		curr_page += 1
	"""
		
compute_analytics_data()