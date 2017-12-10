import bottlenose
import xml.etree.ElementTree as ET
import json
from time import sleep
from keyword_generator import generate_new_searches
import os.path
import random

TRAVIS_AMAZON_ACCESS_KEY = 'AKIAJTUR54KXVNE7S5PA'
TRAVIS_AMAZON_SECRET_KEY = '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'
TRAVIS_AMAZON_ASSOC_TAG = 'foorev-20'



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

	def refresh_instances():
		print("refreshing")
		self.amazon_search_instances = self.instances_waiting_for_refresh + self.amazon_search_instances
		self.instances_waiting_for_refresh = []

	def item_search(self, keywords, item_page):
		if (len(self.amazon_search_instances) == 0):
			self.refresh_instances()

		current_instance = self.amazon_search_instances[0]
		response = current_instance.item_search_with_retry(keywords, item_page, retry=1)
		if not response:
			print("didn't get a response (most likely rate limit, but possibly parse error. moving current\
				account to end of queue and starting over with a new account. probably will skip this.")
			instance_to_refresh = current_instance
			self.amazon_search_instances.pop(0)
			self.instances_waiting_for_refresh.append(instance_to_refresh)

		return response



class AmazonSearch:
	def __init__(self, AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG):
		self.AMAZON_ACCESS_KEY = AMAZON_ACCESS_KEY
		self.AMAZON_SECRET_KEY = AMAZON_SECRET_KEY
		self.AMAZON_ASSOC_TAG = AMAZON_ASSOC_TAG
		self.MAX_RETRY = 5
		self.api = bottlenose.Amazon(AMAZON_ACCESS_KEY, AMAZON_SECRET_KEY, AMAZON_ASSOC_TAG)

	def item_search_with_retry(self, keywords, item_page, retry=1):
		try:
			response = self.api.ItemSearch(Keywords=keywords, SearchIndex="Apparel", BrowseNode="9056987011", ItemPage=item_page)
			#print(response)
			return response
		except Exception as e:
			if retry > self.MAX_RETRY:
				return None
			print("retry", e, retry)
			sleep(1)
			self.item_search_with_retry(keywords, item_page, retry=retry+1)



def parse_item_search_response(response):
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

def get_tshirt_products_for_keyword(keyword):
	postfix_variants = ["tshirt"]
	all_items = []
	# iterate through first 10 pages
	for item_page in range(1, 10):
		for postfix in postfix_variants:
			item_page = str(item_page)

			# @TODO make this dynamic
			accounts = [{
				"access_key": TRAVIS_AMAZON_ACCESS_KEY,
				"secret_key": TRAVIS_AMAZON_SECRET_KEY,
				"assoc_tag": TRAVIS_AMAZON_ASSOC_TAG
			}]
			api = AmazonSearchWithRotatingAccounts(accounts)
			response = api.item_search('{} {}'.format(keyword, postfix), item_page)
			if not response:
				print("fucked up")
				continue
			items = parse_item_search_response(response)
			print [item["title"] for item in items]
			all_items += items

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

def get_existing_keywords():
	if not os.path.exists("keywords.txt"):
		return set()
	f = open("keywords.txt", "r")
	keywords = f.readlines()[1:-1]
	keywords = [k.strip() for k in keywords]
	f.close()
	return set(keywords)

def get_existing_asins():
	asins = set()
	f = open("data.txt", "r")
	data = f.readlines()[0:-1]
	for row in data:
		asin = row.strip().split(',')[0]
		asins.add(asin)
	return asins


# @TODO: Phrases with more than 1 word are not respected here
REMOVE_WORDS = ['cape', 'crewneck', 'v-neck', 'jersey', 'short sleeve',
'pocket', 'crew neck', 'workwear', 'sportswear', 'sleeveless', 'sport', 
'socks', 'crew', 'hoodie', 'polo', 'jacket', 'socks', 'pants', 'jeans', 
'hanes', 'fruit of the loom', 'athletic', 'performance', 'long sleeve', 
'cotton', 'pant', 'sock', 'sleeve', 'cape', 'big and tall', 'plain', 'basic',
'fitted', 'crew-neck']


def bootstrap_initial_data():
	
	all_items = get_tshirt_products_for_keyword("")
	if os.path.exists("data.txt"):
		datafile = open("data.txt", "a")
		existing_asins = get_existing_asins()
	else:
		datafile = open("data.txt", "w+")
		existing_asins = set()
	f = open("keywords.txt", "w+")
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

		row = generate_row(item)
		datafile.write(row + "\n")
		existing_asins.add(asin)

		new_searches = generate_new_searches(title)
		for search in new_searches:
			print("writing to keywords")
			f.write(search + "\n")
	f.close()










# CALL THIS FUNCTION ONLY WHEN KEYWORDS.TXT AND DATA.TXT ARE EMPTY!!! PLZZZZZZ 
# OTHERWISE YOU WILL OVERWRITE YOUR DATA AND HAVE TO START FROM SCRATCH :( :( :( 
#bootstrap_initial_data()



keywords = list(get_existing_keywords())
random.shuffle(keywords)

# populate new_searches with existing keywords, so you don't trace old keywords you have
# already scraped
# we eventually should weight this depending on staleness of the search
new_searches = set(keywords)
# populate asins 
asins = get_existing_asins()

should_skip_expanding_on_existing_asins = True

f = open("keywords.txt", "a")

if os.path.exists("data.txt"):
	datafile = open("data.txt", "a")
else:
	datafile = open("data.txt", "w+")

for keyword in keywords:
	keyword = keyword.strip()

	all_items = get_tshirt_products_for_keyword(keyword)
	for item in all_items:
		asin = item["asin"].encode('ascii', 'ignore')

		title = item["title"].encode('ascii', 'ignore')
		has_bad_word = False
		for word in REMOVE_WORDS:
			if word in title.lower():
				has_bad_word = True
				break
		if has_bad_word:
			continue

		
		# Turn this on or off depending on wehther you want to expand more, or scrape 
		# more recent info for data you already have
		if should_skip_expanding_on_existing_asins and asin in asins:
			continue
		

		curr_searches = generate_new_searches(title)
		for search in curr_searches:
			if search in new_searches: 
				continue
			new_searches.add(search)
			f.write(search + "\n")

		if asin in asins:
			#@TODO: maybe do this based on the staleness of the file
			continue

		datafile.write(generate_row(item) + "\n")
		asins.add(asin)


datafile.close()
f.close()

