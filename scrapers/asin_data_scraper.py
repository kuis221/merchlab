import os.path
from grab_asin_data import DataCollectorWithRotatingAccounts, reliable_grab_asin_data

if not os.path.exists("asin_data_over_time.txt"):
	datafile = open("asin_data_over_time.txt", "w+")
else:
	datafile = open("asin_data_over_time.txt", "a")


def generate_row(data):
	title = data.get("Title", "").replace(',', '')
	list_price = data.get("ListPrice", {}).get("Amount", "")
	currency = data.get("ListPrice", {}).get("CurrencyCode", "")
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
	salesrank_data = data.get("SalesrankData", {})
	main_category_id = salesrank_data.get("MainSalesrankCategoryId", "")
	main_salesrank = salesrank_data.get(main_category_id, "")
	return ','.join([title, list_price, currency, asin, brand, image, color, studio, genre, manufacturer, 
		publisher, binding, product_group, label, department, product_type_name, part_number, marketplace_id, main_category_id, main_salesrank])	

f = open("data.txt", "r")
data = f.readlines()[0:-1]
rotating_data_collector = DataCollectorWithRotatingAccounts()

for row in data:
	try:
		asin = row.split(',')[0]
		print("hello", asin)
		#print(rotating_data_collector.data_collector.grab_data_for_asin(asin))
		data = reliable_grab_asin_data(rotating_data_collector, asin)
		print(data)
		if not data:
			print("wtf?")
			continue
		print("here")
		generated_row = generate_row(data).encode('ascii', 'ignore')
		datafile.write(generated_row + "\n")
	except Exception as e:
		print(e)
		print("go on to next row")
f.close()