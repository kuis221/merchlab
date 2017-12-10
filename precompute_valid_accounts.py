import firebase_api
from scrapers.grab_asin_data import DataCollector

def get_valid_users():
	users = firebase_api.get_users()
	expired_with_valid_auth_token = []
	for user in users:
		if not user.get("active") and user.get("sellerId") and user.get("authToken"):
			expired_with_valid_auth_token.append(user)

	valid_users = []
	for user in expired_with_valid_auth_token:
		#print("hihii")
		data_collector = DataCollector(user)
		product, error = data_collector.grab_data_for_asin("B0755LLJST")
		if error and "Access to Products.GetMatchingProductForId is denied".lower() in error.get("errorMessage").lower():
		 	# @TODO: Maybe cache these bad accounts somewhere for faster initial loading?
		 	#print("remove that guy")
		 	pass
		elif error and "The seller does not have an eligible Amazon account to call Amazon MWS".lower() in error.get("errorMessage").lower():
			#print("got em")
			pass
		elif error:
			pass
			print("fuck")
			print(error)
		else:
			#print("valid")
		 	valid_users.append(user)
		 	#print(product)
	return valid_users

valid_users = get_valid_users()
firebase_api.update_object("", "validInactiveMwsAccounts", valid_users)
print firebase_api.query_objects("validInactiveMwsAccounts")