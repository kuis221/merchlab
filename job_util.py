import firebase_api
import util
import json
import xml.etree.ElementTree as ET
import datetime
import csv
from psycopg2 import IntegrityError
from scrapers.scraper_v3 import (
	get_tshirt_products_for_keyword,
	REMOVE_WORDS
)
from scrapers.grab_asin_data import reliable_grab_asin_data, DataCollectorWithRotatingAccounts
from scrapers.keyword_generator import generate_new_searches
from analytics_util import compute_analytics_data_for_asins

import boto
import boto.s3
import sys
from boto.s3.key import Key

from scrapers.asin_indexer import get_existing_asins, get_existing_keywords
from models import AsinSnapshot, AsinMetadata, IndexedKeyword, AsinAnalytics
from app import db
from time import sleep
from dynamodb_util import write_snapshot_to_dynamodb, write_trademarks_analysis
import re
from scrapers.trademarks import get_trademarks_analysis, deduplicate_trademarks
import datetime
from datetime import timedelta



def save_scraped_file_in_s3(datestr, filename):
	try:
		AWS_ACCESS_KEY_ID = 'AKIAJNXO62C54H2EOFUA'
		AWS_SECRET_ACCESS_KEY = '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'

		bucket_name = "merchlab-scraper"
		conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
		        AWS_SECRET_ACCESS_KEY)

		print 'Uploading %s to Amazon S3 bucket %s' % \
		   (filename, bucket_name)

		bucket = conn.get_bucket(bucket_name)
		k = Key(bucket)
		k.key = datestr + '/' + filename
		k.set_contents_from_filename(filename)
		print('Upload to S3 succeeded.')
		return True
	except Exception as e:
		print("S3 file upload didn't work")
		print(e)
		return False

def snapshot_asins(asins):
	rotating_data_collector = DataCollectorWithRotatingAccounts()
	print("finished initializing")

	for i, asin in enumerate(asins):
		if i%10 == 0:
			print("Currently on " + str(i) + " of " + str(len(asins)) + " asins")
		
		data = reliable_grab_asin_data(rotating_data_collector, asin)

		if not data:
			print("Couldn't grab data for asin (most likely removed, but may be rate-limited as well). \
				Don't compute asin analytics and don't snapshot it either.", asin)
			continue

		list_price = data.get("ListPrice", {}).get("Amount", None)
		currency_code = data.get("ListPrice", {}).get("CurrencyCode", None)
		main_salesrank_category_id = data.get("SalesrankData", {}).get("MainSalesrankCategoryId", None)
		salesrank = data.get("SalesrankData", {}).get(main_salesrank_category_id)
		timestamp = datetime.datetime.utcnow().isoformat()
		snapshot_data = {
			"list_price": list_price,
			"currency_code": currency_code,
			"salesrank_category": main_salesrank_category_id,
			"salesrank": salesrank,
			"timestamp": timestamp,
			"asin": asin
		}
		snapshot = AsinSnapshot(snapshot_data)
		#db.session.add(snapshot)
		try:
			response = write_snapshot_to_dynamodb(snapshot)
		except Exception as e:
			print(e, response)

		compute_analytics_data_for_asins([asin])
	

	"""
	try:
		db.session.commit()
		print("success")
		return True
	except Exception as e:
		print("it rolled back")
		db.session.rollback()
		print(e)
		return False
	"""


def scrape_from_homepage(search_index="Apparel", browse_node="9056987011"):
	rotating_data_collector = DataCollectorWithRotatingAccounts()
	print("finished initializing")
	#keywords_to_use = choose_keywords(num_keywords=num_keywords, method=method)
	#keywords_to_use = ["cat", "dog", "monkey"]

	# populate new_searches with existing keywords, so you don't trace old keywords you have already scraped
	# we eventually should weight this depending on staleness of the search
	#existing_keywords = set(get_existing_keywords())
	#existing_keywords = set([])

	# populate asins 
	#asins = get_existing_asins()
	#asins = set([])
	further_keywords = set([])

	all_items = get_tshirt_products_for_keyword("", search_index=search_index, browse_node=browse_node)
	print(str(len(all_items)) + " products discovered on homepage")
	for item in all_items:
		asin = item["asin"].encode('ascii', 'ignore')
		title = item["title"].encode('ascii', 'ignore')
		#print(title)
		has_bad_word = False
		for word in REMOVE_WORDS:
			if word in title.lower():
				has_bad_word = True
				break
		if has_bad_word:
			continue

		curr_searches = generate_new_searches(title)
		for search in curr_searches:
			further_keywords.add(search)

		parent_asin = item.get("parent_asin")
		if not parent_asin:
			parent_asin = asin

		data = reliable_grab_asin_data(rotating_data_collector, asin)
		if not data:
			continue

		title = data.get("Title", "").encode('ascii', 'ignore').replace(',', '')

		# Sometimes AWS titles are empty string - double check with mws data to make sure it actually is a valid merch shirt
		has_bad_word = False
		for word in REMOVE_WORDS:
			if word in title.lower():
				has_bad_word = True
				break
		if has_bad_word:
			continue
		else:
			print(title.encode('ascii', 'ignore'))

		asin = data.get("ASIN", "")
		brand = data.get("Brand", "")
		image = data.get("SmallImage", {}).get("URL", "")
		color = data.get("Color", "")
		studio = data.get("Studio", "")
		genre = data.get("Genre", "")
		manufacturer = data.get("Manufacturer", "")
		publisher = data.get("Publisher", "")
		binding = data.get("Binding", "")
		product_group = data.get("ProductGroup", )
		label = data.get("Label", "")
		department = data.get("Department", "")
		product_type_name = data.get("ProductTypeName", "")
		part_number = data.get("PartNumber", "")
		marketplace_id = data.get("MarketplaceId", "")
		timestamp = datetime.datetime.utcnow().isoformat()

		final_data = {
			"title": title.encode('ascii', 'ignore'),
			"asin": asin.encode('ascii', 'ignore'),
			"parent_asin": parent_asin.encode('ascii', 'ignore'),
			"brand": brand.encode('ascii', 'ignore'),
			"image": image.encode('ascii', 'ignore'),
			"color": color.encode('ascii', 'ignore'),
			"studio": studio.encode('ascii', 'ignore'),
			"genre": genre.encode('ascii', 'ignore'),
			"manufacturer": manufacturer.encode('ascii', 'ignore'),
			"publisher": publisher.encode('ascii', 'ignore'),
			"binding": binding.encode('ascii', 'ignore'),
			"product_group": product_group.encode('ascii', 'ignore'),
			"label": label.encode('ascii', 'ignore'),
			"department": department.encode('ascii', 'ignore'),
			"product_type_name": product_type_name.encode('ascii', 'ignore'),
			"part_number": part_number.encode('ascii', 'ignore'),
			"marketplace_id": marketplace_id,
			"discovery_keyword": "",
			"search_index": search_index.encode('ascii', 'ignore'),
			"browse_node": browse_node.encode('ascii', 'ignore'),
			"discovery_timestamp": timestamp
		}

		item = AsinMetadata(data=final_data)
		db.session.add(item)
		try:
			db.session.commit()
			#data_writer.writerow(final_data)
		except Exception as e:
			db.session.rollback()
			if "duplicate key value violates unique constraint" in str(e).lower():
				pass
			else:
				print("this is real error when trying to save asin metadata", e)
		list_price = data.get("ListPrice", {}).get("Amount", None)
		currency_code = data.get("ListPrice", {}).get("CurrencyCode", None)
		main_salesrank_category_id = data.get("SalesrankData", {}).get("MainSalesrankCategoryId", None)
		salesrank = data.get("SalesrankData", {}).get(main_salesrank_category_id)
		snapshot_data = {
			"list_price": list_price,
			"currency_code": currency_code,
			"salesrank_category": main_salesrank_category_id,
			"salesrank": salesrank,
			"timestamp": timestamp,
			"asin": asin
		}
		snapshot = AsinSnapshot(snapshot_data)
		#db.session.add(snapshot)
		try:
			response = write_snapshot_to_dynamodb(snapshot)
		except Exception as e:
			print(e, response)

	# The first argument is supposed to be today_str, but this is deprecated and unused
	# so temporarily hacking through this code by adding None
	scrape_merch_asins_task(None, further_keywords, search_index=search_index, browse_node=browse_node)


def update_keyword_metadata(keyword):
	try:
		# basically this logic here tries to query the keyword and update it, otherwise it
		# tries to create new index for the keyword in DB
		indexed_keyword_item = IndexedKeyword.query.filter_by(id=keyword).first()
		if not indexed_keyword_item:
			keyword_data = {
				"last_indexed_date": datetime.datetime.utcnow().isoformat(),
				"number_of_times_indexed": 1,
				"first_indexed_date": datetime.datetime.utcnow().isoformat()
			}
			keyword_item = IndexedKeyword(keyword_data)
			db.session.add(keyword_item)
			try:
				db.session.commit()
			except Exception as e:
				# @TODO: Log error
				db.session.rollback()
				print(e)
		else:
			if not indexed_keyword_item.number_of_times_indexed:
				indexed_keyword_item.number_of_times_indexed = 1
			else:
				indexed_keyword_item.number_of_times_indexed += 1
			indexed_keyword_item.last_indexed_date = datetime.datetime.utcnow().isoformat()
			try:
				db.session.commit()
			except Exception as e:
				# @TODO: Log error
				db.session.rollback()
				print(e)				

	except Exception as e:
		print(e)
		print("failed to update keyword metadata")

def scrape_merch_asins_task(datestr, keywords_to_use, search_index="Apparel", browse_node="9056987011"):

	rotating_data_collector = DataCollectorWithRotatingAccounts()
	print("finished initializing")
	#keywords_to_use = choose_keywords(num_keywords=num_keywords, method=method)
	#keywords_to_use = ["cat", "dog", "monkey"]

	# populate new_searches with existing keywords, so you don't trace old keywords you have already scraped
	# we eventually should weight this depending on staleness of the search
	#existing_keywords = set(get_existing_keywords())
	#existing_keywords = set([])

	# populate asins 
	#asins = get_existing_asins()
	#asins = set([])

	#keywords_file = open(job_id + "_keywords.csv", "w+")
    #keywords_writer = csv.writer(keywords_file)

	#datafile = open(job_id + "_data.csv", "w+")
	#headers = ['asin', 'product_type_name', 'marketplace_id', 'title', 'color', 'search_index', 'brand', 'publisher', 'binding', 'label', 'parent_asin', 'part_number', 'department', 'studio', 'genre', 'discovery_keyword', 'product_group', 'image', 'browse_node', 'manufacturer']
	#data_writer = csv.DictWriter(datafile, fieldnames=headers)

	# Regex for cleaning special characters and extra spaces
	pattern = re.compile('([^\s\w]|_)+')

	for indx, keyword in enumerate(list(keywords_to_use)):
		print(str(indx) + " out of " + str(len(list(keywords_to_use))))
		keyword = keyword.strip()
		keyword = pattern.sub('', keyword)

		all_items = get_tshirt_products_for_keyword(keyword, search_index=search_index, browse_node=browse_node)
		print(str(len(all_items)) + " products discovered for '" + keyword + "' keyword")
		
		update_keyword_metadata(keyword)

		for item in all_items:
			asin = item["asin"].encode('ascii', 'ignore')
			asin_metadata_row = AsinMetadata.query.filter_by(id=asin).first()
			if asin_metadata_row:
				print("already found item - skip it")
				continue

			title = item["title"].encode('ascii', 'ignore')
			#print(title)
			has_bad_word = False
			for word in REMOVE_WORDS:
				if word in title.lower():
					has_bad_word = True
					break
			if has_bad_word:
				continue

			curr_searches = generate_new_searches(title)
			for search in curr_searches:
				indexed_keyword = IndexedKeyword({"keyword": search})
				db.session.add(indexed_keyword)
				try:
					db.session.commit()
				except Exception as e:
					db.session.rollback()

			#datafile.write(generate_row(item) + "\n")

			parent_asin = item.get("parent_asin")
			if not parent_asin:
				parent_asin = asin

			data = reliable_grab_asin_data(rotating_data_collector, asin)
			if not data:
				continue

			title = data.get("Title", "").encode('ascii', 'ignore').replace(',', '')

			# Sometimes AWS titles are empty string - double check with mws data to make sure it actually is a valid merch shirt
			has_bad_word = False
			for word in REMOVE_WORDS:
				if word in title.lower():
					has_bad_word = True
					break
			if has_bad_word:
				continue
			else:
				print(title.encode('ascii', 'ignore'))

			asin = data.get("ASIN", "")
			brand = data.get("Brand", "")
			image = data.get("SmallImage", {}).get("URL", "")
			color = data.get("Color", "")
			studio = data.get("Studio", "")
			genre = data.get("Genre", "")
			manufacturer = data.get("Manufacturer", "")
			publisher = data.get("Publisher", "")
			binding = data.get("Binding", "")
			product_group = data.get("ProductGroup", )
			label = data.get("Label", "")
			department = data.get("Department", "")
			product_type_name = data.get("ProductTypeName", "")
			part_number = data.get("PartNumber", "")
			marketplace_id = data.get("MarketplaceId", "")
			timestamp = datetime.datetime.utcnow().isoformat()

			final_data = {
				"title": title.encode('ascii', 'ignore'),
				"asin": asin.encode('ascii', 'ignore'),
				"parent_asin": parent_asin.encode('ascii', 'ignore'),
				"brand": brand.encode('ascii', 'ignore'),
				"image": image.encode('ascii', 'ignore'),
				"color": color.encode('ascii', 'ignore'),
				"studio": studio.encode('ascii', 'ignore'),
				"genre": genre.encode('ascii', 'ignore'),
				"manufacturer": manufacturer.encode('ascii', 'ignore'),
				"publisher": publisher.encode('ascii', 'ignore'),
				"binding": binding.encode('ascii', 'ignore'),
				"product_group": product_group.encode('ascii', 'ignore'),
				"label": label.encode('ascii', 'ignore'),
				"department": department.encode('ascii', 'ignore'),
				"product_type_name": product_type_name.encode('ascii', 'ignore'),
				"part_number": part_number.encode('ascii', 'ignore'),
				"marketplace_id": marketplace_id,
				"discovery_keyword": keyword.encode('ascii', 'ignore'),
				"search_index": search_index.encode('ascii', 'ignore'),
				"browse_node": browse_node.encode('ascii', 'ignore'),
				"discovery_timestamp": timestamp
			}

			item = AsinMetadata(data=final_data)
			db.session.add(item)
			try:
				db.session.commit()
				#data_writer.writerow(final_data)
			except Exception as e:
				db.session.rollback()
			print("already found the asin... skipping", item.id)

			list_price = data.get("ListPrice", {}).get("Amount", None)
			currency_code = data.get("ListPrice", {}).get("CurrencyCode", None)
			main_salesrank_category_id = data.get("SalesrankData", {}).get("MainSalesrankCategoryId", None)
			salesrank = data.get("SalesrankData", {}).get(main_salesrank_category_id)
			snapshot_data = {
				"list_price": list_price,
				"currency_code": currency_code,
				"salesrank_category": main_salesrank_category_id,
				"salesrank": salesrank,
				"timestamp": timestamp,
				"asin": asin
			}
			snapshot = AsinSnapshot(snapshot_data)
			#db.session.add(snapshot)
			try:
				response = write_snapshot_to_dynamodb(snapshot)
			except Exception as e:
				print(e, response)

			compute_analytics_data_for_asins([asin])

	

	#datafile.close()
	#keywords_file.close()
	#save_scraped_file_in_s3(datestr, job_id + "_data.csv")
	#save_scraped_file_in_s3(datestr, job_id + "_keywords.csv")



#today_str = str(datetime.datetime.today()).split()[0]
#job_id = "abc"
#scrape_merch_asins_task(today_str, job_id)

def scrape_trademarks_analysis_for_asins(asins):
	for asin in asins:
		try:
			# Get all necessary data for that asin from asin_metadata table
			asin_metadata = AsinMetadata.query.filter_by(id=asin).first()
			asin_analytics = AsinAnalytics.query.filter_by(id=asin).first()

			if not asin_metadata or not asin_analytics:
				continue

			relevant_trademarks = []
			other_trademarks = []

			# @TODO: Add description, features to this job
			title = asin_metadata.title
			brand = asin_metadata.brand
			title_analysis = get_trademarks_analysis(title)
			brand_analysis = get_trademarks_analysis(brand)
			relevant_trademarks += title_analysis.get("relevant_trademarks", [])
			relevant_trademarks += brand_analysis.get("relevant_trademarks", [])
			other_trademarks += title_analysis.get("other_trademarks", [])
			other_trademarks += brand_analysis.get("other_trademarks", [])

			relevant_trademarks = deduplicate_trademarks(relevant_trademarks)
			other_trademarks = deduplicate_trademarks(other_trademarks)

			timestamp = datetime.datetime.utcnow().isoformat()

			# @TODO: Snapshot this in DynamoDB
			data = {
				"asin": asin,
				"relevant_trademarks": relevant_trademarks,
				"other_trademarks": other_trademarks,
				"timestamp": timestamp
			}
			write_trademarks_analysis(data)

			asin_analytics.last_trademark_indexed_date = timestamp

			try:
				db.session.commit()
			except Exception as e:
				db.session.rollback()
				print("rolled back", e)

		except Exception as e:
			print("hit exception while trying to get trademark analysis for asin", asin)
			print("this was error", e)




