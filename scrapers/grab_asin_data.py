import mws_search
from mws_wrapper import mws
import firebase_api
import util
import xml.etree.ElementTree as ET
import mws_pricing
import random

def convert_xml_to_json(root):
	data = {}
	#print(root.keys())
	for key in root.keys():
		data[key] = root.get(key)

	if len(root) == 0:
		 data[root.tag.replace('{http://mws.amazonservices.com/schema/Products/2011-10-01}', '')] = root.text
	else:
		subtree_data = []
		for subtree in root:
			subtree_data.append(convert_xml_to_json(subtree))
		data[root.tag.replace('{http://mws.amazonservices.com/schema/Products/2011-10-01}', '')] = subtree_data

	return data



class DataCollectorWithRotatingAccounts:
	# num_accounts is legacy - we should deprecate it if we get the chance
	def __init__(self, num_accounts=25):

		users = firebase_api.get_valid_inactive_mws_accounts()
		random.shuffle(users)
		self.users = users
		print("number of valid usrs", len(self.users))
		self.waiting_for_refresh = []
		self.data_collector = DataCollector(self.users[0])
		done = False

	def refresh(self):
		print("refreshing", len(self.waiting_for_refresh), len(self.users), self.users[0].get("username"))
		self.waiting_for_refresh += [self.users.pop(0)]
		if self.users == []:
			self.users = self.waiting_for_refresh
			self.waiting_for_refresh = []

		self.data_collector = DataCollector(self.users[0])

	def remove_current_account(self):
		print("num available accounts for mws", len(self.users), self.users)
		self.users.pop(0)



class DataCollector:
	def __init__(self, user):
		self.user = user
		self.seller_id = user.get("sellerId")
		self.auth_token = user.get("authToken")
		self.access_key, self.secret_key = util.get_auth_profile(user.get("authProfile"))
		self.marketplace_id = "ATVPDKIKX0DER"
		self.username = user.get("username")

	def grab_data_for_asin(self, asin):
		products, error = mws_search.get_matching_product_for_id(seller_id=self.seller_id, 
			auth_token=self.auth_token, access_key=self.access_key, secret_key=self.secret_key, 
			marketplaceid=self.marketplace_id, idType="ASIN", id=[asin])

		if error: 
			return None, error	

		if len(products) > 0:
			return products[0], None
		else:
			return None, None

	def grab_lowest_priced_offers_for_asin(self, asin):
		products_api = mws.Products(access_key=self.access_key, secret_key=self.secret_key,
		 account_id=self.seller_id, auth_token=self.auth_token)

		xml = products_api.get_competitive_pricing_for_asin(marketplaceid=self.marketplace_id, asins=[asin]).response.content
		return xml
		#print(xml)

		"""
		xml = products_api.get_lowest_priced_offers_for_asin(marketplaceid=self.marketplace_id, 
			asin=asin, condition="new").response.content
		print(xml)
		root = ET.fromstring(xml)

		data = convert_xml_to_json(root)

		identifier = data['GetLowestPricedOffersForASINResponse'][0]['GetLowestPricedOffersForASINResult'][0]['Identifier']
		summary = data['GetLowestPricedOffersForASINResponse'][0]['GetLowestPricedOffersForASINResult'][1]['Summary']
		offers = data['GetLowestPricedOffersForASINResponse'][0]['GetLowestPricedOffersForASINResult'][2]['Offers']

		data = {}		

		from mws_pricing import parse_identifier, parse_summary, parse_offers

		data.update(parse_identifier(identifier))
		data.update(parse_summary(summary))
		data.update(parse_offers(offers))

		xml = products_api.get_lowest_priced_offers_for_asin(marketplaceid=self.marketplace_id, asin=asin, condition="used").response.content

		root = ET.fromstring(xml)

		api_data = convert_xml_to_json(root)
		offers = parse_offers(api_data['GetLowestPricedOffersForASINResponse'][0]['GetLowestPricedOffersForASINResult'][2]['Offers'])
		return offers
		"""

def reliable_grab_asin_data(rotating_data_collector, asin, max_tries=5):
	#rotating_data_collector = DataCollectorWithRotatingAccounts()
	#asin = "B0755LLJST"

	curr = 0
	while curr < max_tries:
		product, error = rotating_data_collector.data_collector.grab_data_for_asin(asin)
		if error and "Access to Products.GetMatchingProductForId is denied".lower() in error.get("errorMessage").lower():
			curr += 1
			print("removing", error, rotating_data_collector.data_collector.username)
			rotating_data_collector.remove_current_account()
		elif error and "The seller does not have an eligible Amazon account to call Amazon MWS".lower() in error.get("errorMessage").lower():
			curr += 1
			print("removing", error, rotating_data_collector.data_collector.username)
			rotating_data_collector.remove_current_account()
		elif error:
			print("unhandled error", error, rotating_data_collector.data_collector.username)
			curr += 1
			rotating_data_collector.refresh()
		else:
			return product

#asin = "B0755LLJST"
#rotating_data_collector = DataCollectorWithRotatingAccounts()
#print(rotating_data_collector.users)
#print(rotating_data_collector.data_collector.grab_data_for_asin(asin))
#print reliable_grab_asin_data(rotating_data_collector, asin)