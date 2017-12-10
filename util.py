import csv
import io
import random, string

def randomword(length):
   return ''.join(random.choice(string.lowercase) for i in range(length))



def get_auth_profile(profile_name):
	if not profile_name or profile_name.lower() == "jeff":
		access_key = 'AKIAJZ6R7P2H65YKTHLQ' #replace with your access key
		secret_key = 'BDmbHcnfrWCB0i33bMN2YqW13UHG2ptV3s5HYqzs' #replace with your secret key
	elif profile_name.lower() == "travis":
		access_key = 'AKIAJSNVELTOEPBABFSA'
		secret_key = 'YkBHuWfsPqlivbB84VIV4bOCDcDCt38N7JxXAlOv'
	else:
		access_key = None
		secret_key = None
	return access_key, secret_key



def create_tsv(headers, data):
	print(data)
	for indx, row in enumerate(data):
		row = [unicode(r) for r in row]
		data[indx] = row

	output = io.BytesIO()
	writer = csv.writer(output, dialect=csv.excel_tab)
	writer.writerow(headers)
	writer.writerows(data)
	return output.getvalue()


def clean_exported_data_for_tracking_spreadsheet(headers, data):
	cleaned_headers = ['MSKU', 'Source', 'Date code', "ASIN/ISBN/UPC", "Cost per Item", "List Price", "Sales Rank", "Quantity", "Condition", "Description", "Date Shipped", "Shipping Cost", "Ship Cost per Item", "Total Cost", "Total List Price"]
	old_header_to_index = {}
	for indx, header in enumerate(headers):
		old_header_to_index[header] = indx
		print(indx, header)

	new_header_to_index = {}
	for indx, header in enumerate(cleaned_headers):
		new_header_to_index[header] = indx

	"""
	Expected fields for header mapping, exclusive to TheBookFlipper's tracking spreadsheet:
		-dateShipped
		-shippingCost
		-shippingCostPerItem
		-totalCost
		-totalListPrice
	"""

	header_mapping = {
		"SKUNumber": "MSKU",
		"barcodeNumber": "ASIN/ISBN/UPC",
		"price": "List Price",
		"qty": "Quantity",
		"condition": "Condition",
		"note": "Description",
		"dateShipped": "Date Shipped",
		"shippingCost": "Shipping Cost",
		"shipCostPerItem": "Ship Cost per Item",
		"totalCost": "Total Cost",
		"totalListPrice": "Total List Price",
		"source": "Source",
		"costPerItem": "Cost per Item",
		"salesrank": "Sales Rank"
	}

	old_to_new_index = {}
	for old_header in header_mapping:
		old_index = old_header_to_index[old_header]
		new_header = header_mapping[old_header]
		new_index = new_header_to_index[new_header]
		old_to_new_index[old_index] = new_index

	cleaned_data = []
	for row in data:
		cleaned_row = [""]*len(cleaned_headers)
		for indx, cell in enumerate(row):
			if indx not in old_to_new_index:
				continue

			new_index = old_to_new_index[indx]
			cleaned_row[new_index] = cell

		cleaned_data.append(cleaned_row)

	tsv_data = create_tsv(cleaned_headers, cleaned_data)
	return tsv_data


def clean_exported_data(headers, data):
	cleaned_headers = ['sku', 'product-id', 'product-id-type', 'price', 'minimum-seller-allowed-price', 'maximum-seller-allowed-price', 'item-condition', 'quantity', 'add-delete', 'will-ship-internationally', 'expedited-shipping', 'standard-plus', 'item-note', 'fulfillment-center-id', 'product-tax-code']

	old_header_to_index = {}
	for indx, header in enumerate(headers):
		old_header_to_index[header] = indx
		print(indx, header)

	new_header_to_index = {}
	for indx, header in enumerate(cleaned_headers):
		new_header_to_index[header] = indx

	header_mapping = {
		"SKUNumber": "sku",
		"barcodeNumber": "product-id",
		"barcodeType": "product-id-type",
		"price": "price",
		"qty": "quantity",
		"condition": "item-condition",
		"note": "item-note",
		"minSellerAllowedPrice": "minimum-seller-allowed-price",
		"maxSellerAllowedPrice": "maximum-seller-allowed-price",
		"fulfillmentCenterId": "fulfillment-center-id"
	}

	product_id_type_mapping = {
		"ASIN": "1",
		"ISBN": "2",
		"UPC": "3",
		"EAN": "4"
	}

	item_condition_mapping = {
		"Used / Like New": "1",
		"Used / Very Good": "2",
		"Used / Good": "3",
		"Used / Acceptable": "4",
		"Collectible / Like New": "5",
		"Collectible / Very Good": "6",
		"Collectible / Good": "7",
		"Collectible / Acceptable": "8",
		"Not Used": "9",
		"Refurbished": "10",
		"New": "11"
	}

	old_to_new_index = {}
	for old_header in header_mapping:
		old_index = old_header_to_index[old_header]
		new_header = header_mapping[old_header]
		new_index = new_header_to_index[new_header]
		old_to_new_index[old_index] = new_index

	cleaned_data = []
	for row in data:
		cleaned_row = [""]*len(cleaned_headers)
		for indx, cell in enumerate(row):
			if indx not in old_to_new_index:
				continue

			new_index = old_to_new_index[indx]

			if headers[indx] == 'condition' and cell in item_condition_mapping:
				print("Cell", cell)
				cleaned_row[new_index] = item_condition_mapping[cell]
				continue

			elif headers[indx] == 'barcodeType' and cell in product_id_type_mapping:
				cleaned_row[new_index] = product_id_type_mapping[cell]
				continue

			cleaned_row[new_index] = cell

		cleaned_data.append(cleaned_row)

	tsv_data = create_tsv(cleaned_headers, cleaned_data)
	return tsv_data
