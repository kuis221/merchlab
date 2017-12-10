import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

from mws_wrapper import mws
import xml.etree.ElementTree as ET
import time
import inspect
import barcodenumber

# Developer Credentials
ACCESS_KEY = 'AKIAJZ6R7P2H65YKTHLQ' #replace with your access key
SECRET_KEY = 'BDmbHcnfrWCB0i33bMN2YqW13UHG2ptV3s5HYqzs' #replace with your secret key

# US ONLY currently - this will change soon
marketplace_id="ATVPDKIKX0DER"

#Temporary erchant credentials - ONLY for testing
"""
merchant_id = 'A1SDJYL8XER1WH' #replace with your merchant id
auth_token = "amzn.mws.bca9e498-7960-fcde-23fe-564202360a55"
"""

def parse_products_from_api(api_obj):
	xml = api_obj.response.content
	#print(xml)
	root = ET.fromstring(xml)
	products_result = root[0]
	products = products_result[0]
	results = []
	for product in products:
		product_data = {}
		if len(product) == 0:
			continue
		identifiers = product[0]

		"""STEP 1: Parse the identifiers"""

		for identifier in identifiers:
			if identifier.tag.split('}')[1] == 'MarketplaceASIN':
				for identifier_key_elem in identifier:
					identifier_key = identifier_key_elem.tag.split('}')[1]
					identifier_val = identifier_key_elem.text
					product_data[identifier_key] = identifier_val
				break

		"""STEP 2: Parse the attributes"""
		try:
			attributes_set = product[1]
			item_attributes = attributes_set[0]
			for attribute in item_attributes:
				tag = attribute.tag.split('}')[1]

				# no child in xml etree, so this must be the child attribute element
				if len(attribute) == 0:
					text = attribute.text
					product_data[tag] = text
					continue

				# here, if this code executes, that means there were children attributes for the current
				# attribute (i.e. dimensions has child attributes like height, width, etc.)
				metadata = {}
				for meta_attr in attribute:
					metatag = meta_attr.tag.split('}')[1]
					metadata[metatag] = meta_attr.text

				product_data[tag] = metadata
		except Exception as e:
			print("Failed parsing the attributes", e)

		"""STEP 3: Parse the sales rankings"""
		sales_rankings = product[3]
		#print("IM HERE")

		if len(sales_rankings) > 0:
			main_category_id = sales_rankings[0][0].text
			rank_dict = {}
			rank_dict["MainSalesrankCategoryId"] = main_category_id
			for rank_data in sales_rankings:

				#rank_data = sales_rankings[0]
				productCategoryId, rank = rank_data[0].text, rank_data[1].text
				rank_dict[productCategoryId] = rank

			product_data["SalesrankData"] = rank_dict
		#print(product_data)
		results.append(product_data)
	return results

def hmap_product(product):
	hmapped_product = {}
	hmapped_product["ASIN"] = product["ASIN"]
	hmapped_product["name"] = product["Title"]
	hmapped_product["itemDimensions"] = product.get("ItemDimensions")
	hmapped_product["packageDimensions"] = product.get("PackageDimensions")

	if "Binding" in product:
		hmapped_product["binding"] = product["Binding"]
	
	if "ProductGroup" in product:
		hmapped_product["category"] = product["ProductGroup"]
	
	if "SmallImage" in product and "URL" in product["SmallImage"]:
		hmapped_product["imageUrl"] = product["SmallImage"]["URL"]

	if "Rank" in product:
		hmapped_product["salesrank"] = product["Rank"]
	return hmapped_product

def list_matching_products(seller_id, auth_token, access_key, secret_key, marketplaceid, query, curr_try=1, max_try=2):
	products_api = mws.Products(access_key=access_key, secret_key=secret_key, account_id=seller_id, auth_token=auth_token)
	
	try:
		matching_products_obj = products_api.list_matching_products(marketplaceid=marketplaceid, query=query)
		products = parse_products_from_api(matching_products_obj)

		# TMP - Reconcile later
		#map headers to our version for the frontend 

		hmapped_products = []
		#print(products[0])
		for product in products:
			hmapped_product = hmap_product(product)
			hmapped_products.append(hmapped_product)

		return hmapped_products
	except Exception as e:
		try:
			print(e)
			root = ET.fromstring(str(e))
			error = root[0]
			error_type = error[0].text
			code = error[1].text
			error_message = error[2].text
			if code == "AccessDenied":
				return {"errorType": error_type, "errorCode": code, "errorMessage": error_message}
			else:
				if curr_try >= max_try:
					return hmapped_products
				else:
					return list_matching_products(seller_id, auth_token, access_key, secret_key, marketplaceid, query, curr_try+1, max_try)
		except Exception as e:
			if curr_try >= max_try:
				return []
			else:
				return list_matching_products(seller_id, auth_token, access_key, secret_key, marketplaceid, query, curr_try+1, max_try)			




def get_matching_product_for_id(seller_id, auth_token, access_key, secret_key, marketplaceid, idType, id):
	try: 
		products_api = mws.Products(access_key=access_key, secret_key=secret_key, account_id=seller_id, auth_token=auth_token)
		matching_products_obj = products_api.get_matching_product_for_id(marketplaceid=marketplaceid, type=idType, ids=id)
		products = parse_products_from_api(matching_products_obj)

		# TMP - Reconcile later
		#map headers to our version for the frontend 

		hmapped_products = []
		for product in products:
			#hmapped_product = hmap_product(product)
			hmapped_products.append(product)

		return hmapped_products, None
	except Exception as e:
		#print(e)
		try:
			root = ET.fromstring(str(e))
			error = root[0]
			error_type = error[0].text
			code = error[1].text
			error_message = error[2].text
			return None, {"errorType": error_type, "code": code, "errorMessage": error_message}
		except Exception as e:
			return None, {"errorType": "unknown", "code": "unknown", "errorMessage": "unknown"}


# Extremely stupid method for validating: make a sample API call, and return False if there's an exception
def is_valid_auth_data(seller_id, auth_token, access_key, secret_key):
	print("at the validation stage!!!!")
	products_api = mws.Products(access_key=access_key, secret_key=secret_key, account_id=seller_id, auth_token=auth_token)
	try: 
		matching_products_obj = products_api.get_matching_product_for_id(marketplaceid="ATVPDKIKX0DER", type="ISBN", ids=["0470500972"])
		products = parse_products_from_api(matching_products_obj)
		first = products[0]
		x = ("ASIN: " + first["ASIN"])
		x = ("Publisher: " + first["Publisher"])
		x = ("Rank: " + first["Rank"])
		x = ("ProductCategoryId: " + first["ProductCategoryId"])
		x = ("Title: " + first["Title"])
		x = ("Image: " + first["SmallImage"]["URL"])
		x = ("ProductTypeName: " + first["ProductTypeName"])
		return True
	except Exception as e:
		print(e)
		return False

def could_be_asin(barcode):
	return barcode.isalnum() and len(barcode) == 10

def get_id_type(barcode):
	if barcode.isdigit():

		# could be UPC/ISBN
		barcode_split = str(barcode)
		odd_chars = barcode_split[0:-1][::2]
		even_digits = barcode_split[1:-1][::2]

		sum_odd = sum(map(lambda x: int(x), odd_chars))
		sum_even = sum(map(lambda x: int(x), even_digits))


		if len(barcode_split) == 10:
			check_sum = 0
			for index, elem in enumerate(barcode_split):
				check_sum += int(barcode_split[index]) * (10-index)
			if check_sum % 11 == 0:
				return "ISBN"
		elif len(barcode_split) == 13:
			check_sum = (sum_even * 3) + sum_odd
			check_digit = check_sum % 10 if (check_sum%10 == 0) else 10-(check_sum%10)
			if check_digit == barcode_split[-1]:
				return "ISBN"

		check_sum = (sum_odd * 3) + sum_even
		check_digit = (check_sum % 10)
		if check_digit != 0:
			check_digit =10-check_digit
		if check_digit == int(barcode_split[-1]):
			return "UPC"

		if barcodenumber.check_code('ean13', barcode_split):
			return "EAN"
		if barcodenumber.check_code('ean', barcode_split):
			return "EAN"

def convert_textbook_ean_to_isbn13(barcode):
	if not barcode.isdigit():
		return None

	barcode_split = str(barcode)
	without_check_digit = barcode_split[0:-1]
	modified_first_three = '978' + without_check_digit[3:]
	odd_chars = modified_first_three[0:][::2]
	even_digits = modified_first_three[1:][::2]
	sum_odd = sum(map(lambda x: int(x), odd_chars))
	sum_even = sum(map(lambda x: int(x), even_digits))
	#print(barcode_split, modified_first_three, odd_chars, even_digits, sum_odd, sum_even)
	total = sum_odd + sum_even*3
	if total % 10 == 0:
		check_digit = 0
	else:
		check_digit = 10 - (total % 10)
	print(modified_first_three + str(check_digit))
	return modified_first_three + str(check_digit)