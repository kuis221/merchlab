import bottlenose
import xml.etree.ElementTree as ET
import json
from time import sleep
from keyword_generator import generate_new_searches
import os.path
import random
from grab_asin_data import reliable_grab_asin_data
from models import IndexedKeyword
from dynamodb_util import write_keyword_snapshot_to_dynamodb, write_asin_keywords
import random
import datetime

ACCOUNTS = []

f = open("scrapers/credentials.csv", "r")
rows = f.readlines()[1:-1]
for row in rows:
	row = row.strip('\n').split(",")[0:-1]
	assoc_tag = row[3]
	access_key = row[4]
	secret_key = row[5]
	if assoc_tag == '' or access_key == '' or secret_key == '':
		continue
	ACCOUNTS.append({
		'assoc_tag': assoc_tag,
		'access_key': access_key,
		'secret_key': secret_key
	})

print(len(ACCOUNTS))


class AmazonSearchWithRotatingAccounts:
	def __init__(self, accounts):
		self.accounts = accounts
		amazon_search_instances = []
		for account in accounts:
			access_key = account.get("access_key")
			secret_key = account.get("secret_key")
			assoc_tag = account.get("assoc_tag")
			amazon_search_instances.append(AmazonSearch(access_key, secret_key, assoc_tag))

		self.instances_waiting_for_refresh = []
		self.amazon_search_instances = amazon_search_instances

	def refresh_instances(self):
		self.amazon_search_instances = self.instances_waiting_for_refresh + self.amazon_search_instances
		self.instances_waiting_for_refresh = []

	def item_search(self, keywords, item_page, search_index="Apparel", browse_node="9056987011"):
		if (len(self.amazon_search_instances) == 0):
			self.refresh_instances()

		current_instance = self.amazon_search_instances[0]
		print("Current account: " + current_instance.AMAZON_ASSOC_TAG)


		success = False
		curr_try = 0
		max_try = 5
		response = None
		while not success and curr_try < max_try:
			try:
				response = current_instance.item_search_with_retry(keywords, item_page, search_index=search_index, browse_node=browse_node)
				if response:
					success = True
				else:
					print("didn't get a response (most likely rate limit, but possibly parse error. moving current\
						account to end of queue and starting over with a new account. probably will skip this.")
					instance_to_refresh = current_instance
					self.amazon_search_instances.pop(0)
					self.instances_waiting_for_refresh.append(instance_to_refresh)
			except Exception as e:
				pass
			curr_try += 1


		return response



class AmazonSearch:
	def __init__(self, AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG):
		self.AMAZON_ACCESS_KEY = AMAZON_ACCESS_KEY
		self.AMAZON_SECRET_KEY = AMAZON_SECRET_KEY
		self.AMAZON_ASSOC_TAG = AMAZON_ASSOC_TAG
		self.MAX_RETRY = 1
		self.api = bottlenose.Amazon(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

	def item_search_with_retry(self, keywords, item_page, search_index="Apparel", browse_node="9056987011", retry=0):
		try:
			response = self.api.ItemSearch(Keywords=keywords, SearchIndex=search_index, BrowseNode=browse_node, ItemPage=item_page)
			#print(response)
			return response
		except Exception as e:
			if retry > self.MAX_RETRY:
				return None
			#print("and here")
			print("retry", e, retry)
			return self.item_search_with_retry(keywords, item_page, retry=retry+1)



def parse_item_search_response(response):
	print(response)
	root = ET.fromstring(response)
	total_pages = int(root[1][2].text)
	print(total_pages)
	items = root[1][4:]
	cleaned_items = []
	for item in items:
		try:
			asin = item[0].text
			parent_asin = item[1].text
			detail_page_url = item[2].text
			#item_links = item[3]
			if len(item) < 5:
				item_attributes = []
				manufacturer = None
				product_group = None
			else:
				item_attributes = item[4]
				manufacturer = item_attributes[0].text
				product_group = item_attributes[1].text

			if (len(item_attributes) < 3):
				title = ""
			else:
				title = item_attributes[2].text
			item_dict = {
				"asin": asin,
				"parent_asin": parent_asin,
				"detail_page_url": detail_page_url,
				"manufacturer": manufacturer,
				"product_group": product_group,
				"title": title
			}
			cleaned_items.append(item_dict)
		except Exception as e:
			print(e)
			print("failed to parse item response")

	return cleaned_items

def remove_duplicate_shirts(shirts):
	# we assume that same asin = same shirt
	asin_to_shirt = {}
	for shirt in shirts:
		asin = shirt["asin"]
		asin_to_shirt[asin] = shirt
	return asin_to_shirt.values()

def get_tshirt_products_for_keyword(keyword, search_index="Apparel", browse_node="9056987011", postfix_variants=["tshirt"]):

	# @TODO make this load accounts dynamically
	random.shuffle(ACCOUNTS)
	api = AmazonSearchWithRotatingAccounts(ACCOUNTS)

	all_items = []
	# iterate through first 10 pages

	for postfix in postfix_variants:
		position_to_asin_mapping = {}
		for item_page in range(1, 11):
			print("item page", item_page)
			item_page = str(item_page)

			response = api.item_search('{} {}'.format(keyword, postfix), item_page, search_index=search_index, browse_node=browse_node)
			if not response:
				print("fucked up")
				continue
			items = parse_item_search_response(response)
			
			# Generate Mapping of keyword position to asin for this keyword
			for indx, item in enumerate(items):
				current_position = (int(item_page)-1)*10 + (indx+1)
				position_to_asin_mapping[current_position] = item["asin"]
			#print [item["title"] for item in items]
			all_items += items
		keyword_snapshot = {
			"keyword": '{} {}'.format(keyword, postfix),
			"position_mapping": json.dumps(position_to_asin_mapping),
			"timestamp": datetime.datetime.utcnow().isoformat()
		}
		write_keyword_snapshot_to_dynamodb(keyword_snapshot)
	all_items = remove_duplicate_shirts(all_items)
	return all_items

def generate_row(item, headers=['asin', 'title', 'parent_asin', 'product_group', 'detail_page_url', 'manufacturer']):
	row_list = []
	for header in headers:
		try:
			val = item.get(header, "").encode('ascii', 'ignore')
		except Exception as e:
			val = ""
		row_list.append(val)
	return ','.join(row_list)


# @TODO: Phrases with more than 1 word are not respected here
REMOVE_WORDS = ['cape', 'crewneck', 'v-neck', 'jersey', 'short sleeve',
'pocket', 'crew neck', 'workwear', 'sportswear', 'sleeveless', 'sport', 
'socks', 'crew', 'hoodie', 'polo', 'jacket', 'socks', 'pants', 'jeans', 
'hanes', 'fruit of the loom', 'athletic', 'performance', 'long sleeve', 
'cotton', 'pant', 'sock', 'sleeve', 'cape', 'big and tall', 'plain', 'basic',
'fitted', 'crew-neck', 'v neck', 'vneck', 'vee tee']


def bootstrap_initial_data():
	
	all_items = get_tshirt_products_for_keyword("")
	if os.path.exists("bootstrap_data.txt"):
		#datafile = open("bootstrap_data.txt", "a")
		existing_asins = get_existing_asins()
	else:
		#datafile = open("bootstrap_data.txt", "w+")
		existing_asins = set()
	f = open("bootstrap_keywords.txt", "w+")
	for item in all_items:

		title = item["title"].encode('ascii', 'ignore')
		has_bad_word = False
		for word in REMOVE_WORDS:
			if word in title.lower():
				has_bad_word = True
				break
		if has_bad_word:
			continue
		print(title)

		asin = item.get("asin")
		if not asin or asin in existing_asins:
			continue

		#row = generate_row(item)
		
		#datafile.write(row + "\n")
		existing_asins.add(asin)

		new_searches = generate_new_searches(title)
		for search in new_searches:
			print("writing to keywords")
			f.write(search + "\n")
	f.close()


# CALL THIS FUNCTION ONLY WHEN KEYWORDS.TXT AND DATA.TXT ARE EMPTY!!! PLZZZZZZ 
# OTHERWISE YOU WILL OVERWRITE YOUR DATA AND HAVE TO START FROM SCRATCH :( :( :( 
#bootstrap_initial_data()


