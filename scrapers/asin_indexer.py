import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from app import db
from models import AsinMetadata, IndexedKeyword
import csv
import boto
import boto.s3
from boto.s3.key import Key
import firebase_api

def get_existing_asins():
	existing_asins = set()
	asins = AsinMetadata.query.with_entities(AsinMetadata.id).all()
	for asin_tup in asins:
		asin = asin_tup[0]
		existing_asins.add(asin)
	return existing_asins

def get_existing_keywords():
	existing_keywords = set()
	keywords = IndexedKeyword.query.with_entities(IndexedKeyword.id).all()
	for keyword_tup in keywords:
		keyword = keyword_tup[0]
		existing_keywords.add(keyword)
	return existing_keywords

def download_file_from_s3(datestr, filename):
	try:
		AWS_ACCESS_KEY_ID = 'AKIAJNXO62C54H2EOFUA'
		AWS_SECRET_ACCESS_KEY = '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'

		bucket_name = "merchlab-scraper"
		conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
		        AWS_SECRET_ACCESS_KEY)

		print 'Downloading %s from Amazon S3 bucket %s' % \
		   (filename, bucket_name)

		bucket = conn.get_bucket(bucket_name)
		k = Key(bucket)
		k.key = datestr + '/' + filename
		file = k.get_contents_as_string()
		return file
	except Exception as e:
		print("S3 file download didn't work")
		print(e)
		return None


def download_merch_data_in_s3(datestr, job_id):
	data_filename = job_id + "_data.csv"
	keywords_filename = job_id + "_keywords.csv"

	try:
		data = download_file_from_s3(datestr, data_filename)
		f = open(data_filename, "w+")
		f.write(data)
		f.close()
		keywords = download_file_from_s3(datestr, keywords_filename)
		f = open(keywords_filename, "w+")
		f.write(keywords)
		f.close()
	except Exception as e:
		print(e)
		print("couldn't download file", datestr, job_id)

def import_local_merch_data_into_db(datestr, job_id, force=False, should_post=False):
	download_merch_data_in_s3(datestr, job_id)
	job_metadata = firebase_api.query_objects("scrape_merch_asin_task/" + datestr + "/" + job_id)
	print(job_metadata, "hello")

	# Have this code logic so that we can do imports for files without jobs attached to them
	if should_post and not job_metadata:
		return
	else:
		job_metadata = {}

	if not force and job_metadata.get("status") == "processed":
		return

	try:
		data = open(job_id + "_data.csv", "r")
		keywords = open(job_id + "_keywords.csv", "r")
	except Exception as e:
		print(e)
		return False

	headers = ['asin', 'product_type_name', 'marketplace_id', 'title', 'color', 'search_index', 'brand', 'publisher', 'binding', 'label', 'parent_asin', 'part_number', 'department', 'studio', 'genre', 'discovery_keyword', 'product_group', 'image', 'browse_node', 'manufacturer']
	data_reader = csv.reader(data)
	for row in data_reader:
		data_dict = {}
		for i, header in enumerate(headers):
			data_dict[header] = row[i]
		
		if not data_dict.get("asin"):
			continue
		
		item = AsinMetadata(data=data_dict)
		db.session.add(item)
		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print("already found the asin... skipping", item.id)

	for row in keywords.readlines()[0:-1]:
		keyword = row.strip('\n')
		indexed_keyword = IndexedKeyword(data={"keyword": keyword})
		db.session.add(indexed_keyword)

		try:
			db.session.commit()
		except Exception as e:
			db.session.rollback()
			print("it rolled back")

	if should_post == True:
		firebase_api.update_object("scrape_merch_asin_task/" + datestr, job_id, {"status": "processed"})
	return True


#download_merch_data_in_s3("2017-10-14", "-KwTa5v1v0yHWstaMJIR")
#import_local_merch_data_into_db("2017-10-14", "-KwTa5v1v0yHWstaMJIR", force=False, should_post=True)
