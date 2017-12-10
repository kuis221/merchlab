import requests
from keyword_generator import generate_new_searches
import json

username = "merchlab"
password = "hFNgq26j4c"


DEFAULT_DESCRIPTION_MATCHES = ['t-shirt', 'shirt', 'tank top', 'halter top', 'sweater', 'sweatshirt', 'hooded sweatshirt', 'coat', 
'jersey', 'jacket', 'bottom', 'pant', 'trouser', 'jean', 'short', 'sweatpant', 'pajama', 'sock', 'dresse', 
'skirt', 'blouse', 'underwear', 'swimwear', 'headwear', 'footwear', 'sleepwear', 'pantie', 'boxer', 'jacket', 
'hat', 'vest', 'legging', 'glove', 'beanie', "clothing", "apparel", "sweater", "fashion", "tshirt", "t shirt", "teeshirt"]


# we need to be smarter about how to include these as relevant, because lots of other words can contain this pattern of characters
secondary = ['hat', 'top', 'tee', 'entertainment']

def get_trademarks_for_term(term):
	url = "https://www.markerapi.com/api/v1/trademark/search/{}/username/{}/password/{}".format(term, username, password)
	response = requests.get(url)
	trademarks_data = json.loads(response.content)
	count = trademarks_data.get("count", 0)
	try:
		count = int(count)
	except Exception as e:
		return []

	if count == 0:
		return []

	trademarks = trademarks_data.get("trademarks")
	return trademarks

def get_trademarks_analysis(string, description_matches=DEFAULT_DESCRIPTION_MATCHES):
	trademarks = []
	relevant_trademarks = []
	other_trademarks = []

	string = ''.join(ch for ch in string if ch.isalnum() or ch == ' ')
	searches = generate_new_searches(string)
	for search in searches:
		print(search)
		curr_trademarks = get_trademarks_for_term(search)
		trademarks += curr_trademarks

	for trademark in trademarks:
		try:
			match_found = False
			for description_match in description_matches:
				description = trademark.get("description", "")
				if description_match.lower() in description:
					match_found = True
					break

			if match_found:
				relevant_trademarks.append(trademark)
			else:
				other_trademarks.append(trademark)
		except Exception as e:
			print(e)
			print("this is failing trademark", trademark)

	return {
		"relevant_trademarks": relevant_trademarks,
		"other_trademarks": other_trademarks
	}

def deduplicate_trademarks(trademarks):
	deduped = []
	serial_numbers = set()

	for trademark in trademarks:
		serial = trademark.get("serialnumber")
		if serial in serial_numbers:
			continue
		deduped.append(trademark)
	return deduped

"""
print get_trademarks_analysis(
	"It's Accrual World Distressed Funny Math Accounting", 
	description_matches
)
"""