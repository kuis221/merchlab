import firebase_api
from app import hash_pass

new_password = "MerchByAmazon"
user = firebase_api.find_user_by_username("Soulfire86")
firebase_api.update_object("users/" + user["objectId"],"password", hash_pass(new_password))