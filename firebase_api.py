import time
import uuid

from firebase import firebase
import datetime

# CONFIG
db_url = "https://merchlab-31696.firebaseio.com/"

# APP SETUP - DO NOT TOUCH
fb = firebase.FirebaseApplication(db_url, authentication=None)


def get_valid_inactive_mws_accounts():
	db_url = "https://blinding-heat-2796.firebaseio.com/"
	fb = firebase.FirebaseApplication(db_url, authentication=None)
	users = fb.get('/validInactiveMwsAccounts', None)
	return users
	
def signup(username, password, email, referrerId=None, customerId=None, plan=None, active=False, isTrialing=False, isDesigner=False, defaults=None):

	data = {
		"username": username,
		"password": password,
		"email": email,
		"role": "user",
		"confirmed": False,
		"referrerId": referrerId,
		"plan": plan,
		"active": active,
		"isTrialing": isTrialing,
		"customerId": customerId,
		"defaults": defaults,
		"isDesigner": isDesigner,
		"authProfile": "travis"
	}

	user_result = save_object('users', data)
	return user_result

def va_signup(username, password, email):
	data = {
		"username": username,
		"password": password,
		"email": email,
		"is_virtual_assistant": True,
	}

	user_result = save_object('users', data)
	return user_result


def login(username, password):
    usersDict = query_objects('users')
    for objectId in usersDict:
        user = usersDict[objectId]
        if "username" not in user:
            print("username NOT IN USER")
            continue

        if user["username"].lower() == username.lower() and user["password"] == password:
            return user
    return None


def find_user_by_customerId(customerId):
    usersDict = query_objects('users')
    if not usersDict:
        return None

    for objectId in usersDict:
        user = usersDict[objectId]
        if "username" not in user:
            continue

        user["objectId"] = objectId
        if "customerId" in user and user["customerId"] == customerId:
            return user

    return None


def find_user_by_sellerId(sellerId):
    usersDict = query_objects('users')
    if not usersDict:
        return None

    for objectId in usersDict:
        user = usersDict[objectId]
        if "username" not in user:
            continue

        user["objectId"] = objectId

        if "sellerId" in user and user["sellerId"] == sellerId:
            return user

    return None


def find_user_by_username(username):
    usersDict = query_objects('users')

    if not usersDict:
        return None

    for objectId in usersDict:
        user = usersDict[objectId]
        if "username" not in user:
            continue

        user["objectId"] = objectId
        if user["username"].lower() == username.lower():
            user["objectId"] = objectId
            return user


def find_user_by_email(email):
    usersDict = query_objects('users')

    if not usersDict:
        return None

    for objectId in usersDict:
        user = usersDict[objectId]
        if "username" not in user:
            continue

        user["objectId"] = objectId
        if user["email"].lower() == email.lower():
            user["objectId"] = objectId
            return user


def find_user_by_object_id(object_id):
    user = query_objects('users/' + object_id)
    if user:
        user["objectId"] = object_id
        return user


def find_all_users_by_email(email):
    found_users = []
    usersDict = query_objects('users')

    if not usersDict:
        return None

    for objectId in usersDict:
        user = usersDict[objectId]
        if "username" not in user:
            continue

        user["objectId"] = objectId
        if user["email"].lower() == email.lower():
            user["objectId"] = objectId
            found_users.append(user)
    return found_users


def delete_user(username):
    pass


# Saves an object into Parse.com.
def save_object(class_name, data):
    if "createdAt" not in data:
        data["createdAt"] = time.time()

    result = fb.post('/' + class_name, data)
    return result


def update_object(class_name, object_id, data):
    fb.put('/' + class_name, name=object_id, data=data,
           params={'print': 'silent'})


def update_object_and_get_result(class_name, object_id, data):
    fb.put('/' + class_name, name=object_id, data=data)


def patch_object(url, data):
    result = fb.patch(url, data=data)
    return result


# Finds all object instances in Parse with given class_name, and given query.
def query_objects(class_name):
    result = fb.get('/' + class_name, None)
    return result


def get_users():
    users_dict = query_objects("users")
    users = []
    for object_id in users_dict:
        user = users_dict[object_id]
        user["objectId"] = object_id
        users.append(user)
    return users


def get_active_users():
    users = get_users()
    users = [u for u in users if u.get("active") and u.get("sellerId") and u.get("authToken")]
    return users


def update_password(username, new_password):
    user = find_user_by_username(username)
    result = patch_object("users/" + user["objectId"], {"password": hash_pass(new_password)})
    return "success"


def update_password_by_email(email, new_password):
    user = find_user_by_email(email)
    result = patch_object("users/" + user["objectId"], {"password": hash_pass(new_password)})
    return "success"


def update_username(username, new_username):
    user = find_user_by_username(username)
    result = patch_object("users/" + user["objectId"], {"username": new_username})
    return "success"


def update_seller_id(username, seller_id):
    user = find_user_by_username(username)
    result = patch_object("users/" + user["objectId"], {"sellerId": seller_id})
    return "success"


def create_password_reset_token(email):
    user = find_user_by_email(email)
    token = str(uuid.uuid4())
    update_object('password_reset_tokens', user['objectId'], {'token': token, 'expiration_date': (datetime.datetime.utcnow() + datetime.timedelta(hours=1)).isoformat()})
    return token


def get_password_reset_token_by_email(email):
    """
    Given email address, return stored password reset token, if it exists. If not, return None

    :param email: email address to get token for;
    :return: str with UUID token if it exists, otherwise None
    """
    user = find_user_by_email(email)
    result = fb.get('password_reset_tokens/{0}'.format(user['objectId']), None)
    if result:
        return result.get('token')
    else:
        return None


def get_user_by_password_reset_token(token):
    """
    Given UUID token, return User dict if found one. If not, return None

    :param token: str -> UUID token;
    :return: dict with User data if it exists, otherwise None
    """
    results = query_objects('password_reset_tokens')
    for user_object_id in results:
        db_token = results[user_object_id].get('token')
        if db_token and db_token == token:
            if "expiration_date" not in results[user_object_id] or datetime.datetime.utcnow() > results[user_object_id]["expiration_date"]:
                return None

            return find_user_by_object_id(user_object_id)

    return None


SPECIAL_CHARACTER_MAPPING = {
    '.': '\_PERIOD_CHAR',
    '$': '\_DOLLAR_SIGN',
    '#': '\_HASHTAG_SIGN',
    '[': '\_LEFT_SQUARE_BRACKET',
    ']': '\_RIGHT_SQUARE_BRACKET',
    '/': '\_FORWARD_SLASH'
}


def clean_string_for_firebase(string):
    for char in SPECIAL_CHARACTER_MAPPING:
        cleaned_char = SPECIAL_CHARACTER_MAPPING[char]
        string = string.replace(char, cleaned_char)
    return string


def decode_firebase_encoded_string(string):
    reverse_mapping = {}
    for key in SPECIAL_CHARACTER_MAPPING:
        reverse_mapping[SPECIAL_CHARACTER_MAPPING[key]] = key

    for char in reverse_mapping:
        decoded_char = reverse_mapping[char]
        string = string.replace(char, decoded_char)
    return string
