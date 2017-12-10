import sys
import os
sys.path.insert(1, os.path.join(sys.path[0], '..'))

import firebase_api

users = firebase_api.get_users()

expired_with_valid_auth_token = []

for user in users:
	if not user.get("active") and user.get("sellerId") and user.get("authToken"):
		expired_with_valid_auth_token.append(user)

print(len(expired_with_valid_auth_token))