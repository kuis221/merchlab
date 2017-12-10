import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from mws_wrapper import mws
import xml.etree.ElementTree as ET
import time
import inspect


# Developer Credentials
ACCESS_KEY = 'AKIAJZ6R7P2H65YKTHLQ' #replace with your access key
SECRET_KEY = 'BDmbHcnfrWCB0i33bMN2YqW13UHG2ptV3s5HYqzs' #replace with your secret key


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


def convert_xml_to_json_v2(root):
	data = {}
	#print(root.keys())
	for key in root.keys():
	 	data[key] = root.get(key)

	if len(root) == 0:
		 return root.text
	else:
		tag = root.tag.replace('{http://mws.amazonservices.com/schema/Products/2011-10-01}', '')

		# this if statement executes if list exists in the tag, and is not the word listing
		if 'list' in tag.lower().replace('listing', ''):
			subtree_list = []
			for subtree in root:
				#print(convert_xml_to_json_v2(subtree))
				subtree_list.append(convert_xml_to_json_v2(subtree))
				#data[root.tag.replace('{http://mws.amazonservices.com/schema/Products/2011-10-01}', '')] = subtree_data
			return subtree_list
		else:
			for subtree in root:
				subtree_tag = subtree.tag.replace('{http://mws.amazonservices.com/schema/Products/2011-10-01}', '')

				data[subtree_tag] = convert_xml_to_json_v2(subtree)

	return data


def merge_list_of_dicts(list_of_dicts):
	return_dict = {}
	for elem in list_of_dicts:
		return_dict.update(elem)
	return return_dict

def parse_identifier(identifier):
	identifierDict = {}
	for attribute in identifier:
		for attribute_key in attribute:
			identifierDict[attribute_key] = attribute[attribute_key]

	print(identifierDict)
	timeOfOfferChange = identifierDict.get("TimeOfOfferChange")
	itemCondition = identifierDict.get("ItemCondition")
	marketplaceId = identifierDict.get("MarketplaceId")

	return {
		"timeOfOfferChange": timeOfOfferChange,
		"itemCondition": itemCondition,
		"marketplaceId": marketplaceId
	}

def parse_summary(summary):
	summaryDict = {}

	for attribute in summary:
		pass
		#print(attribute)
		#summaryDict[attribute.keys()[0]] = attribute[attribute.keys()[0]]
		summaryDict.update(attribute)

	totalOfferCount = summaryDict.get("TotalOfferCount")
	listPrice = summaryDict.get("ListPrice")
	numberOfOffers = summaryDict.get("NumberOfOffers")
	buyBoxEligibleOffers = summaryDict.get("BuyBoxEligibleOffers")

	buyBoxPrices = summaryDict.get("BuyBoxPrices")
	return {
		"totalOfferCount": totalOfferCount,
		"listPrice": listPrice,
		"numberOfOffers": numberOfOffers,
		"buyBoxEligibleOffers": buyBoxEligibleOffers,
		"buyBoxPrices": buyBoxPrices
	}

def parse_offers(offers):
	"""
	Returns a list of offers that are parsed
	"""

	if not offers:
		return {
			"offers": []
		}

	offerDictList = []

	for offer in offers:
		offerDict = {}
		for attribute in offer['Offer']:
			offerDict[attribute.keys()[0]] = attribute[attribute.keys()[0]]

		if "ShipsFrom" in offerDict:
			offerDict["ShipsFrom"] = merge_list_of_dicts(offerDict["ShipsFrom"])

		if "Shipping" in offerDict:
			offerDict["Shipping"] = merge_list_of_dicts(offerDict["Shipping"])

		if "ListingPrice" in offerDict:
			offerDict["ListingPrice"] = merge_list_of_dicts(offerDict["ListingPrice"])

		if "SellerFeedbackRating" in offerDict:
			offerDict["SellerFeedbackRating"] = merge_list_of_dicts(offerDict["SellerFeedbackRating"])

		offerDictList.append(offerDict)

	return {
		"offers": offerDictList
	}




def parse_fees_estimate(xml):
	root = ET.fromstring(xml)
	#print(xml)

	#print 
	data = convert_xml_to_json_v2(root)

	parsed_fees_list = []

	if not data.get("GetMyFeesEstimateResult") or not data["GetMyFeesEstimateResult"].get("FeesEstimateResultList"):
		return parsed_fees_list

	fee_estimate_result_list = data["GetMyFeesEstimateResult"]["FeesEstimateResultList"]

	for fee_estimate_result in fee_estimate_result_list:
		print(fee_estimate_result)
		if "FeesEstimate" not in fee_estimate_result:
			if "Error" in fee_estimate_result:	
				code = 	fee_estimate_result["Error"].get("Code")
				message = fee_estimate_result["Error"].get("Message")
				error_type = fee_estimate_result["Error"].get("Type")
				parsed_fees_list.append({
					"totalFeeEstimate": "0.00",
					"feeCurrencyCode": "USD",
					"fees": [],
					"error": code + " - " + error_type + " - " + message
				})
			else:
				parsed_fees_list.append({
					"totalFeeEstimate": '0.00',
					"feeCurrencyCode": 'USD',
					"fees": [],
					"error": "FeesEstimate not found, but there was no error message. Unexpected problem."
				})				
		try:
			total_fee_amount = fee_estimate_result["FeesEstimate"]["TotalFeesEstimate"]["Amount"]
			total_fee_currency_code = fee_estimate_result["FeesEstimate"]["TotalFeesEstimate"]["CurrencyCode"]

			fees = []
			for fee_detail_item in fee_estimate_result["FeesEstimate"]["FeeDetailList"]:
				fee_type = fee_detail_item["FeeType"]
				fee_amount = fee_detail_item["FinalFee"]["Amount"]
				fee_currency_code = fee_detail_item["FinalFee"]["CurrencyCode"]
				fees.append({
					"feeType": fee_type, 
					"feeAmount": fee_amount,
					"feeCurrencyCode": fee_currency_code
				})

			parsed_fees_list.append({
				"totalFeeEstimate": total_fee_amount,
				"feeCurrencyCode": total_fee_currency_code,
				"fees": fees,
				"error": None
			})
			print(fees)
		except Exception as e:
			#print(xml)
			parsed_fees_list.append({
				"totalFeeEstimate": "0.00",
				"feeCurrencyCode": "USD",
				"fees": [],
				"error": str(e)
			})

	print("got here bro", parsed_fees_list)

	return parsed_fees_list


def get_my_fees_estimate_for_asin(seller_id, auth_token, access_key, secret_key, asin, is_amazon_fulfilled, identifier, listing_price, listing_currency_code, 
	shipping_price="0.00", shipping_currency_code="USD", marketplace_id="ATVPDKIKX0DER", curr_try=1, max_try=3):
	
	try:
		item = convert_data_to_item(asin, is_amazon_fulfilled, identifier, listing_price, listing_currency_code, shipping_price, \
			shipping_currency_code, marketplace_id)

		products_api = mws.Products(access_key=access_key, secret_key=secret_key, account_id=seller_id, auth_token=auth_token)
		xml = products_api.get_my_fees_estimate(feesEstimateRequestList=[item]).response.content

		parsed_fees_list = parse_fees_estimate(xml)
		return parsed_fees_list[0]

	except KeyError as e:
		print("its a key error", e)
		print(xml)
		return {}
	except Exception as e:
		print(e, item)
		if curr_try == max_try:
			return {}

		time.sleep(1)
		return get_my_fees_estimate_for_asin(seller_id, auth_token, asin, is_amazon_fulfilled, identifier, listing_price, listing_currency_code, 
			shipping_price=shipping_price, shipping_currency_code=shipping_currency_code, marketplace_id=marketplace_id, curr_try=curr_try+1, max_try=max_try)


# Bulk function deisgned to estimate orders 20 at a time
def get_my_fees_estimate_for_orders(seller_id, auth_token, access_key, secret_key, orders):
	if len(orders) > 4:
		return
	
	items = []
	for order in orders:
		asin = order.asin
		is_amazon_fulfilled = order.fulfillment_channel == "Amazon"
		identifier = "test1"
		item_price = order.item_price or "0.00"
		item_currency_code = order.currency or "USD"
		shipping_price = order.shipping_price or "0.00"
		shipping_currency_code=order.currency or "USD"

		item = convert_data_to_item(asin, is_amazon_fulfilled, identifier, item_price, item_currency_code,\
			shipping_price, shipping_currency_code)
		items.append(item)

	try:
		products_api = mws.Products(access_key=access_key, secret_key=secret_key, account_id=seller_id, auth_token=auth_token)
		xml = products_api.get_my_fees_estimate(feesEstimateRequestList=items).response.content
		parsed_fees_list = parse_fees_estimate(xml)
		#print(parsed_fees_list)
		return parsed_fees_list
	except Exception as e:
		print("Shit! There was an error.", e)
		return None





# Helper function to get item in a format to get fees estimate
# Used for get_my_fees_estimate_for_asin, get_my_fees_estimate_for_orders
def convert_data_to_item(asin, is_amazon_fulfilled, identifier, item_price, item_currency_code, 
	shipping_price="0.00", shipping_currency_code="USD", marketplace_id="ATVPDKIKX0DER"):
	
	item = {
		"MarketplaceId": marketplace_id,
		"IdType": "ASIN",
		"IdValue": asin,
		"Identifier": identifier,
		"PriceToEstimateFees": {
			"ListingPrice": {
				"CurrencyCode": item_currency_code,
				"Amount": item_price
			},
			"Shipping": {
				"CurrencyCode": shipping_currency_code,
				"Amount": shipping_price
			}
		}
	}

	if is_amazon_fulfilled:
		item["IsAmazonFulfilled"] = "true"
	else:
		item["IsAmazonFulfilled"] = "false"	
	return item
