from rq import Queue
from worker import conn
import datetime
from datetime import timedelta
import firebase_api
from scrapers.asin_indexer import import_local_merch_data_into_db

q = Queue(connection=conn)

# iterate over last seven days and do any job that was missing
curr = datetime.datetime.today()
num_days = 7

i = 0 
while i < num_days:
	print("hi", i)
	datestr = str(curr).split()[0]
	jobs_dict = firebase_api.query_objects("scrape_merch_asin_task/" + datestr)
	if not jobs_dict:
		curr = curr - timedelta(days=1)
		i += 1
		continue
	for job_id in jobs_dict:
		if jobs_dict[job_id].get("status") != "uploaded":
			continue
		force = False
		should_post = True
		args = (datestr, job_id, force, should_post)
		print(job_id, datestr)
		q.enqueue_call(import_local_merch_data_into_db, args=args, timeout=3600)
	curr = curr - timedelta(days=1)
	i += 1
