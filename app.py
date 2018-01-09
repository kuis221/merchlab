from flask import Flask, render_template, request, redirect, make_response, url_for
from flask.ext.sqlalchemy import SQLAlchemy
from rq import Queue
from worker import conn
import os
import logging
import sys
from flask_login import (LoginManager, login_required, login_user, 
						 current_user, logout_user)


import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from scrapers.keyword_generator import generate_bigrams, generate_trigrams, turn_ngrams_into_searches

from itsdangerous import URLSafeTimedSerializer
import firebase_api
import md5
import stripe
#Intercom
import hmac
import hashlib

from datetime import timedelta
import datetime
import util
from scrapers import mws_search
import json
#from sync.sync_util import sync_constants, generic_util
#import strategy_util

q = Queue(connection=conn)

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

app.config["REMEMBER_COOKIE_DURATION"] = timedelta(days=14)
app.config["hmac"] = hmac
app.config["hashlib"] = hashlib


#Flask-Login Login Manager
login_manager = LoginManager()
login_manager.login_view = "/login/"
login_manager.init_app(app)

stripe.api_key = "sk_live_troL1NlysCarz4MUW1Myyjw8"
#sk_live_gRlcBUp9pY6NqJcZpbeVLU7f

db = SQLAlchemy(app)
import models
from dynamodb_util import get_snapshots, get_tracked_keywords_for_asin, get_trademarks_for_asin

from keyword_analyzer import get_trending_tshirt_keywords, get_best_seller_keywords, get_keywords_from_titles


def alchemyencoder(obj):
	import decimal
	"""JSON encoder function for SQLAlchemy special classes."""
	if isinstance(obj, datetime.date):
		return obj.isoformat()
	elif isinstance(obj, decimal.Decimal):
		return float(obj)

#Login_serializer used to encryt and decrypt the cookie token for the remember
#me option of flask-login
login_serializer = URLSafeTimedSerializer(app.secret_key)


@app.route("/stripe/hooks/", methods=["POST"])
def stripe_hooks():
	event_json = request.json


	if event_json["id"] != "evt_00000000000000":
		try:
			event = stripe.Event.retrieve(event_json["id"])
		except Exception as e:
			print("fuck, something went wrong.")
			return "failure"

	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


	event_type = event_json["type"]
	print(now + " - Event Type: " + event_type)

	"""
	See here for more info: https://stripe.com/docs/subscriptions/guide#webhooks
	For initial release, we will be implementing the following web hooks:

	customer.created
	customer.subscription.created
	invoice.created
	charge.succeeded (immediate attempt for the first invoice)
	invoice.payment_succeeded
	invoice.payment_failed

	"""
	if event_type == "customer.subscription.deleted":
		try:
			customerId = event_json["data"]["object"]["source"]["customer"]

			user = firebase_api.find_user_by_customerId(customerId)
			if not user:
				# @TODO: Raise Exception, customer was not found
				return "User with that customerId could not be not found."
			firebase_api.update_object("users/" + user["objectId"], "active", False)			
		except Exception as e:
			print("cancel customer failure")

	if event_type == "invoice.payment_failed":
		# send notification to customer that the payment failed
		pass

	if event_type == "invoice.payment_succeeded":
		amount_as_float = None
		user = None
		#is_active = 
		just_completed_trial = False
		try:
			print("I AM EXECUTING")
			#print(event_json)
			# Update the referrer's data
			# Send email to customer
			# set user.invoiceStatus = "confirmed"
			customerId = event_json["data"]["object"]["customer"]
			user = firebase_api.find_user_by_customerId(customerId)

			if not user:
				# @TODO: Raise Exception, customer was not found
				return "User with that customerId could not be not found."


			is_active = firebase_api.query_objects("users/" + user["objectId"] + "/active")
			is_trialing = firebase_api.query_objects("users/" + user["objectId"] + "/isTrialing")

			# Have this code here to fix some bad data conveniently, if it is bad
			if not is_active:
				is_active = True
				firebase_api.update_object("users/" + user["objectId"], "active", True)

			if is_trialing == None:
				is_trialing = False
				firebase_api.update_object("users/" + user["objectId"], "isTrialing", False)

			firebase_api.update_object("stripe_hook_log", "commissionStatus", "after user status handling")

			amount = str(event_json["data"]["object"]["amount_due"])
			amount_as_float = float(event_json["data"]["object"]["amount_due"])/100.0
			amount = "$" + amount[0:-2] + "." + amount[-2:] + " USD"

			if amount_as_float > 0 and is_trialing:
				just_completed_trial = True
				is_trialing = False
				firebase_api.update_object("users/" + user["objectId"], "isTrialing", False)


		except Exception as e:
			print("email failure")

	return "success"





@app.route("/", methods=["GET", "POST"])
def landing():
	return redirect(url_for("register"))

@app.route("/login/", methods=["GET", "POST"])
def login():

	if not current_user.is_anonymous:
		return redirect(url_for("index"))

	if request.method == 'POST':
		print(request.form)
		username = request.form.get("username")
		password = request.form.get("password")
		remember = request.form.get("remember") == "on"

		if '@' in username:
			email = username
			user = firebase_api.find_user_by_email(email)
		else:
			user = firebase_api.find_user_by_username(username)

		if not user:
			return render_template("login.html", error="credentials_error")    

		object_id = user.get("objectId")
		# NOTE: Users are now allowed to sign in through their email
		# User.get method automatically figures out if it's an email or username,
		# based on whether there is an @ in the username string
		user = models.User.get(object_id)
		if user and hash_pass(request.form['password']) == user.password:
			login_user(user, remember=True)
			return redirect(request.args.get("next") or url_for("index"))
	return render_template("login.html")



@app.route("/logout/")
def logout_page():
	"""
	Web Page to Logout User, then Redirect them to Index Page.
	"""
	logout_user()
	return redirect("/")


@app.route("/membership/")
@login_required
def membership():
	userId = current_user.username
	userDetails = firebase_api.find_user_by_username(userId)

	if "customerId" in userDetails:
		customerId = userDetails["customerId"]
		customer = stripe.Customer.retrieve(customerId)

		if len(customer["sources"]["data"]) == 0:
			source = None
		else:
			source = customer["sources"]["data"][0]

		subscription = None
		if len(customer["subscriptions"]["data"]) == 0:
			print("fuck its empty!!!")
		else:
			subscription = customer["subscriptions"]["data"][0]

	else:
		customer = None
		source = None
		subscription = None
	return render_template("membership.html", source=source, subscription=subscription, userDetails=userDetails)

@app.route("/update_billing/", methods=["POST"])
@login_required
def update_billing():
	userId = current_user.username
	userDetails = firebase_api.find_user_by_username(userId)

	stripeToken = request.form.get('stripeToken')

	if "customerId" in userDetails:
		customerId = userDetails["customerId"]
		customer = stripe.Customer.retrieve(customerId)
		
		if len(customer["sources"]["data"]) != 0:
			source = customer["sources"]["data"][0]
			sourceId = source["id"]
			try:
				customer.sources.retrieve(sourceId).delete()
			except Exception as e:
				return "failure"
		try:
			result = customer.sources.create(source=stripeToken)
		except Exception as e:
			print("yeah it failed here")
			print(e)
			return "card_data_error"


		return "success"

	# Customer hasn't been created yet. We need to create a new customer ID
	# Give them the 6 month beta trial, because this means that they were created
	# using the old form.
	try: 
		# Create a Customer
		if "wasCoreBetaTester" in userDetails and userDetails["wasCoreBetaTester"] == True:
			trial_end = datetime.datetime.today()+ relativedelta(months=6)
		else:
			trial_end = datetime.datetime.today()+ relativedelta(weeks=2)	
					
		trial_end = trial_end.strftime("%s")


		customer = stripe.Customer.create(
		  source=stripeToken,
		  plan="accelerlist_pro_plan",
		  email=current_user.email,
		  trial_end=trial_end
		)

		customerId = customer["id"]
		firebase_api.update_object("users/" + userDetails["objectId"], "customerId", customerId)
		firebase_api.update_object("users/" + userDetails["objectId"], "active", True)
		firebase_api.update_object("users/" + userDetails["objectId"], "isTrialing", True)

	except Exception as e:
		print(e)
		print("we are at the error")
		return "card_data_error"

	return "success"


@app.route("/restart_membership/")
@login_required
def restart_membership():
	userId = current_user.username
	userDetails = firebase_api.find_user_by_username(userId)

	if "customerId" in userDetails:
		customerId = userDetails["customerId"]
		customer = stripe.Customer.retrieve(customerId)

		customer.subscriptions.create(plan="accelerlist_pro_plan", trial_end="now")
		firebase_api.update_object("users/" + userDetails["objectId"], "active", True)
		firebase_api.update_object("users/" + userDetails["objectId"], "isTrialing", False)

	return redirect(url_for("membership"))	

@app.route("/cancel_membership/")
@login_required
def cancel_membership():
	userId = current_user.username
	userDetails = firebase_api.find_user_by_username(userId)

	if "customerId" in userDetails:
		customerId = userDetails["customerId"]
		customer = stripe.Customer.retrieve(customerId)

		subscription = None
		if len(customer["subscriptions"]["data"]) == 0:
			print("fuck its empty!!!")
		else:
			subscription = customer["subscriptions"]["data"][0]
			subscriptionId = subscription["id"]
			# NOTE: Only temporarily use this for testing... eventually we want to
			# cancel trial at period end
			customer.subscriptions.retrieve(subscriptionId).delete()
			#customer.subscriptions.retrieve(subscriptionId).delete(at_period_end=True)
			firebase_api.update_object("users/" + userDetails["objectId"], "active", False)
			firebase_api.update_object("users/" + userDetails["objectId"], "isTrialing", False)

	return redirect(url_for("membership"))

def hash_pass(password):
	"""
	Return the md5 hash of the password+salt
	"""
	salted_password = password + app.secret_key
	return md5.new(salted_password).hexdigest()


def round_to_nearest_fifty(x):
	return x + (50 - x) % 50


@app.route("/register/wordcandy/", methods=["GET", "POST"])
def register_wordcandy():

	if not current_user.is_anonymous:
		return redirect(url_for('index'))

	if request.method == 'GET':
		return render_template('register_wordcandy.html')

	username = request.form.get('username')
	password = hash_pass(request.form.get('password'))
	email = request.form.get('email')
	access_code = request.form.get('accessCode')

	print(request.form)

	if username == "" or password == "" or email == "":
		return render_template('register_wordcandy.html', error="required_field_missing")

	if access_code != "WORDCANDY<3MERCHLAB":
		return render_template('register_wordcandy.html', error="The access code you provided is wrong.")

	valid_emails = set(['thebuyersden@gmail.com', 'ajvalewrites@gmail.com', 'successalignedmarketing@gmail.com', '88milesperhourllc@gmail.com', 'jgarza5254@gmail.com', 'nicholso@wpbt.org', 'rherr308@gmail.com', 'devens@email.com', 'PAMELACRAWFORD46@aol.com', 'janetsherill@yahoo.com.au', 'paulk@thesmartestgroup.com', 'omarj@osrandolphgroup.com', 'aries.cucueco@gmail.com', 'paypal@ruffideas.com', 'Stephen.Dalchow@OutbreakCA.com', 'second.chance.5@hotmail.com', 'swissmarket56@gmail.com', 'bookkiosk@att.net', 'hollyannehelder@gmail.com', 'carnietools2@gmail.com', 'payments@greatazdeals.com', 'postier@gmail.com', 'douglas@watchthisinteractive.com', 'dspyres@gmail.com', 'sales@apoogs.com', 'cj004e4367@blueyonder.co.uk', 'jsmilford@gmail.com', 'kpmille2@yahoo.com', 'slwbuy@windstream.net', 'kimmiekid1@gmail.com', 'billing@inde5.com', 'kwright0315@gmail.com', 'soulfire86@gmail.com', 'matt@industryportals.net', 'chrismaddox3d@gmail.com', 'jpavacic@yahoo.com', 'AhhChooy@comcast.net', 'paypal@healthyuhappyu.com', 'csfanatikdbz@gmail.com', 'pmacygyn@teksavvy.com', 'calgarywordpresswebdesign@gmail.com', 'calgarywordpresswebdesign@gmail.com', 'jonplechaty@live.com', 'linda@kidsconsignmentsales.com', 'thebillingexchange@gmail.com', 'Lisa.zuber1@yahoo.com', 'lisabarber2009@gmail.com', 'lollydahlen@gmail.com', 'hprinzrfs@yahoo.com', 'kwkelly53@gmail.com', 'connieoregon@gmail.com', 'cgh.filter@gmail.com', 'jbeckloff@gmail.com', 'jim@cargoczar.com', 'samohtsales@gmail.com', 'tdldoorman@msn.com', 'silvertc15@gmail.com', 'drsrinivasu@gmail.com', 'markapeele@gmail.com', 'micheleli525@gmail.com', 'shelley.miyahara@gmail.com', 'mishmashmara@gmail.com', 'aryeh.download@gmail.com', 'simplelifesolutions@yahoo.com', 'pickman323@gmail.com', 'incomelearningresources@gmail.com', 'lesliemeek8@gmail.com', 'scott@conservelabs.com', 'got.airedales@gmail.com', 'visionarena@gmail.com', 'cw123ch@yahoo.com', 'from.allan@gmail.com', 'dougm@parsaver.com', 'info@colin-henderson.co.uk', 'lrb26@hotmail.com', 'richera@live.com', 'djwsleds@gmail.com', 'thebenfrederick@gmail.com', 'villa34@aol.com', 'samimsuleiman@gmail.com', 'cpstoneham@hotmail.com', 'boris@schaaper.nl', 'diamond_d_lux@yahoo.com', 'nicolevanderhoop@mac.com', 'ebonniebuckley@gmail.com', 'annazaks@hotmail.com', 'alpinemed@yahoo.com', 'barkjax@gmail.com', 'shanefish2000@hotmail.com', 'fullon@hotmail.com', 'marcelino3d@hotmail.com', 'FUNGEAR2015@GMAIL.COM', 'merchtshirt@gmail.com', 'matthias.morel@gmail.com', 'jfarrar1967@yahoo.com', 'dsreminga@charter.net', 'dealmarketalpha@gmail.com', 'kmgproducts@kmgproductsllc.com', 'kellyww@gmail.com', 'jvmcnamee@frontier.com', 'subtidal.creations@gmail.com', 'wschac1@gmail.com', 'cheukyor@yahoo.com', 'dmmoreno@hotmail.com', 'cbuzz2@yahoo.com', 'buyer@ddeco.us', 'eclipsesourcing@outlook.com', 'ballsofswag@gmail.com', 'yfedee@gmail.com', 'senderic@gmail.com', 'npintech@gmail.com', 'robbychen18@gmail.com', 'michael@thecoleys.com', 'xckicks@aol.com', 'yjyee1808@gmail.com', 'LARRYSPRKS@GMAIL.COM', 'LARRYSPRKS@GMAIL.COM', 'support@brickshub.com', 'kiminfo2012@gmail.com', 'annabeckfba@gmail.com', 'bteehan@gmail.com', 'chgarr@aol.com', 'joeybonacia@comcast.net', 'eclixirllc@gmail.com', 'jetzmarket@gmail.com', 'lillian_dueiri@yahoo.com', 'zhenurik@hotmail.com', 'monicawatson@yahoo.com', 'solteq@gmail.com', 'nhowse@sympatico.ca', 'kentburns@kmkbsales.com', 'jcthreetimes@gmail.com', 'cwoodson28@yahoo.com', 'tlstuff@cox.net', 'bggivens@gmail.com'])
	other_valid_emails = ['perpetual360@gmail.com', 'mrdata2001@gmail.com', 'joann@bubbadahsbuys.com', 'jd.lloyd@yahoo.com', 'admin@good4businesses.co.uk', 'carl@good4businesses.co.uk', 'Mattcolvin@gmail.com', 'mycreativeself365@gmail.com', 'maddmanny@gmail.com', 'vitaliy@buzztactix.com', 'vitaliymalanchuk@gmail.com', 'starr10uk@gmail.com', 'starr10uk@gmail.com', 'mdizel@yahoo.com', 'ruschetv@mail.ru', 'xraynat@gmail.com', 'jeffmyers409@gmail.com', 'westcoastmerchandisellc@gmail.com', 'd.bernreiter@gmail.com', 'sctes@hotmail.com', 'ripcitymarketplace@gmail.com', 'prantalam@gmail.com', 'pepjo3@bellsouth.net', 'vadajocorpusa@gmail.com', 'MusicReadingSavantStore@gmail.com', 'peojo3@bellsouth.net', 'aviles.kevin@gmail.com', 'sixfigbiz2002@yahoo.com', 'ripcitymarketplace@gmail.com', 'bellystickerdesigns@gmail.com', 'gmcferrin@icloud.com', 'jebizz@gmx.com', 'mobilizme@gmail.com']
	for e in other_valid_emails:
		valid_emails.add(e.lower())

	if (email.lower() not in valid_emails):
		return render_template('register_wordcandy.html', error="That email does not look like a Wordcandy lifetime email! Try a different email.")

	elif email.lower() not in valid_emails and ("mail.ru" in email or "163.com" in email or "yeah.net" in email):
		return render_template('register_wordcandy.html', error="We cannot process your email address. Please use a different email provider.")

	usersDict = firebase_api.query_objects('users')

	if usersDict:
		for objectId in usersDict:
			user = usersDict[objectId]
			if user["username"].lower() == username.lower():
				result = {"error": "username_exists"}
				return render_template('register_wordcandy.html', error=result["error"])		
			elif user["email"] == email:
				result = {"error": "email_exists"}
				return render_template('register_wordcandy.html', error=result["error"])

	try:
		result = firebase_api.signup(
			username=username, 
			password=password, 
			email=email, 
			customerId=None, 
			plan="wordcandy_lifetime", 
			active=True,
			isTrialing=False
		)

		if "error" in result:
			return render_template('register_wordcandy.html', error=result["error"])

		user = firebase_api.find_user_by_username(username)
		user = models.User(user, [])
		login_user(user)
		return redirect(url_for('thankyou'))
	except Exception as e:
		print(e)
		return render_template('register_wordcandy.html', error="Something unexpected went wrong. Please contact us via our Zendesk email on the top right corner for customer support.")


@app.route("/register/", methods=["GET", "POST"])
def register():

	if not current_user.is_anonymous:
		return redirect(url_for('index'))

	# HACK - PLEASE DO NOT DO THIS LATER ONCE YOU HAVE A LOT OF CUSTOMERS.
	users = firebase_api.get_users()
	num_seats_left = max(10, round_to_nearest_fifty(500 - len(users)))
	num_seats_left = min(50, num_seats_left)

	if request.method == 'GET':
		return render_template('register.html', num_seats_left=num_seats_left)

	print("here")
	referrerId = request.form.get("referrerId")
	username = request.form.get('username')
	password = hash_pass(request.form.get('password'))
	email = request.form.get('email')
	stripeToken = request.form.get('stripeToken')

	print(username, password, email, stripeToken)

	if username == "" or password == "" or email == "":
		return render_template('register.html', num_seats_left=num_seats_left, error="required_field_missing")


	if "mail.ru" in email or "163.com" in email or "yeah.net" in email:
		return render_template('register.html', num_seats_left=num_seats_left, error="We cannot process your email address. Please use a different email provider.")


	usersDict = firebase_api.query_objects('users')

	if usersDict:
		for objectId in usersDict:
			user = usersDict[objectId]
			if user["username"].lower() == username.lower():
				result = {"error": "username_exists"}
				return render_template('register.html', num_seats_left=num_seats_left, error=result["error"])		
			elif user["email"] == email:
				result = {"error": "email_exists"}
				return render_template('register.html', num_seats_left=num_seats_left, error=result["error"])

	try: 
		# Create a Customer
		customer = stripe.Customer.create(
		  source=stripeToken,
		  email=email,
		)
		customerId = customer["id"]

		# Charge 79
		charge = stripe.Charge.create(
			customer=customerId,
			amount=7900,
			currency='usd',
			description='MERCHLAB LIFETIME'
		)
		plan = "lifetime_plan"
	except Exception as e:
		print(e)
		return render_template('register.html', num_seats_left=num_seats_left, error="We had an error processing your card. Please check your CVC and Expiration Date again.")

	try:
		result = firebase_api.signup(
			username=username, 
			password=password, 
			email=email, 
			customerId=customerId, 
			plan=plan, 
			active=True,
			isTrialing=True,
			referrerId=referrerId
		)

		if "error" in result:
			return render_template('register.html', num_seats_left=num_seats_left, error=result["error"])

		user = firebase_api.find_user_by_username(username)
		user = models.User(user, [])
		login_user(user)
		return redirect(url_for('thankyou'))
	except Exception as e:
		print(e)
		return render_template('register.html', num_seats_left=num_seats_left, error="Something unexpected went wrong. Please contact us via our Zendesk email on the top right corner for customer support.")

@app.route("/thankyou/")
@login_required
def thankyou():
	username = current_user.username
	user = firebase_api.find_user_by_username(username)
	print(user)
	customer_id = user.get("customerId")
	if not customer_id:
		return redirect(url_for("index"))
	return render_template("thankyou.html", customer_id=customer_id)

@app.route("/home/")
@login_required
def index():
	print(current_user.user_details, "here")
	return render_template("feed.html")

@app.route("/favorites/")
@login_required
def favorites():
	return render_template("favorites.html")

@app.route("/favorites/data/")
@login_required
def favorites_data():
	favorites = firebase_api.query_objects("merchFavorites/{}".format(current_user.username)) or {}
	asins = set()
	for asin in favorites:
		if favorites[asin] and favorites[asin].get("deleted") == True:
			continue
		asins.add(asin)
	asins = list(asins)
	if not asins or len(asins) == 0:
		return json.dumps({"favorites_list": [], "favorites_by_asin": {}})
	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, 
	asin_analytics.escore, asin_analytics.weighted_escore_v1, 
	asin_analytics.weighted_escore_v2, asin_analytics.streak_score_v1, 
	asin_analytics.streak_score_v2, 
	asin_analytics.list_price, asin_metadata.title, asin_metadata.brand, asin_metadata.image

	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	WHERE asin_analytics.id IN ({})
	ORDER BY asin_analytics.unthrottled_salesrank ASC
	LIMIT 1000;
	""".format(', '.join(["'" + asin + "'" for asin in asins]))

	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[11]
		if "no-img-sm" in image:
			continue
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"escore": row[3],
			"weighted_escore_v1": row[4],
			"weighted_escore_v2": row[5],
			"streak_score_v1": row[6],
			"streak_score_v2": row[7],
			"list_price": row[8],
			"title": row[9],
			"brand": row[10],
			"image": row[11]
		})
	print("processed {} search results".format(len(result)))

	return json.dumps({"favorites_list": result, "favorites_by_asin": favorites})

@app.route("/favorites/add/", methods=["POST"])
@login_required
def add_favorites():
	asin = request.json.get("asin")
	data = {
		"deleted": False,
	}
	firebase_api.update_object("merchFavorites/{}".format(current_user.username), asin, data)
	return json.dumps([])


@app.route("/favorites/delete/", methods=["POST"])
@login_required
def delete_favorites():
	asin = request.json.get("asin")
	data = {
		"deleted": True,
	}
	firebase_api.update_object("merchFavorites/{}".format(current_user.username), asin, data)
	return json.dumps([])

@app.route("/asin_tags/add/", methods=["POST"])
@login_required
def add_asin_tags():
	asin = request.form.get("asin")
	tag = request.form.get("tag")
	curr_asin_tags = firebase_api.query_objects("asinTags/{}/{}".format(current_user.username, asin))
	if not curr_asin_tags:
		curr_asin_tags = []

	curr_asin_tags.append(tag)
	firebase_api.update_object("asinTags/{}".format(current_user.username), asin, data)
	return json.dumps(curr_asin_tags)


def get_bestsellers(query=None):
	query_sql = ""
	if query:
		query_sql = "and lower(asin_metadata.title) like '%%{}%%'".format(query.lower())


	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, asin_analytics.list_price,
	asin_metadata.title, asin_metadata.brand, asin_metadata.image

	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	and asin_analytics.unthrottled_salesrank > 0 and asin_analytics.list_price > 0
	and asin_analytics.unthrottled_salesrank < 10000000
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'

	{}	
	ORDER BY unthrottled_salesrank ASC 
	LIMIT 100;
	""".format(query_sql)

	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[6]
		if "no-img-sm" in image:
			continue
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"list_price": row[3],
			"title": row[4],
			"brand": row[5],
			"image": row[6]
		})
	print("processed {} search results".format(len(result)))
	return result


def get_trending_tshirts_by_metric(metric, query=None, asc=False, filter_zeroes=False):
	query_sql = ""
	if query:
		query_sql = "and lower(asin_metadata.title) like '%%{}%%'".format(query.lower())


	filter_zeros_sql = ""
	if filter_zeroes:
		filter_zeros_sql = "and {} > 0".format(metric)
	order_sql = "DESC"
	if asc:
		order_sql = "ASC"

	min_last_indexed_date = (datetime.datetime.utcnow() - timedelta(days=2)).isoformat()

	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, 
	asin_analytics.escore, asin_analytics.weighted_escore_v1, 
	asin_analytics.weighted_escore_v2, asin_analytics.streak_score_v1, 
	asin_analytics.streak_score_v2, 
	asin_analytics.list_price, asin_metadata.title, asin_metadata.brand, asin_metadata.image,
	asin_metadata.discovery_timestamp

	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	and asin_analytics.unthrottled_salesrank > 0 and asin_analytics.list_price > 0
	and asin_analytics.unthrottled_salesrank < 2000000
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	{}
	and asin_analytics.last_indexed_date > '{}'
	{}	
	ORDER BY {} {} 
	LIMIT 500;
	""".format(filter_zeros_sql, min_last_indexed_date, query_sql, metric, order_sql)

	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[11]
		if "no-img-sm" in image:
			continue
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"escore": row[3],
			"weighted_escore_v1": row[4],
			"weighted_escore_v2": row[5],
			"streak_score_v1": row[6],
			"streak_score_v2": row[7],
			"list_price": row[8],
			"title": row[9],
			"brand": row[10],
			"image": row[11],
			"discovery_timestamp": row[12]
		})
	print("processed {} search results".format(len(result)))
	return result




def get_trending_tshirts_last_7d(query=None):
	
	query_sql = ""
	salesrank_threshold = 300000

	if query:
		query_sql = "and lower(asin_metadata.title) like '%%{}%%'".format(query.lower())
		salesrank_threshold = 1000000

	min_last_indexed_date = (datetime.datetime.utcnow() - timedelta(days=2)).isoformat()

	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, asin_analytics.list_price,
	asin_metadata.title, asin_metadata.brand, asin_metadata.image
	
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	
	WHERE last_7d_salesrank < {} and salesrank < {} and last_1mo_salesrank < 1000000000 
	and asin_analytics.list_price > 0
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	and last_1mo_salesrank/last_7d_salesrank >= 1.2
	and asin_analytics.last_indexed_date > '{}'

	{}

	ORDER BY last_1mo_salesrank/((1+(last_7d_salesrank/100000))*last_7d_salesrank) DESC 
	LIMIT 500;
	""".format(salesrank_threshold, salesrank_threshold, min_last_indexed_date, query_sql)
	print(sql)

	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[6]
		if "no-img-sm" in image:
			continue
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"list_price": row[3],
			"title": row[4],
			"brand": row[5],
			"image": row[6]
		})
	print("processed {} search results".format(len(result)))
	result = sorted(result, key=lambda k: k['salesrank']) 
	return result

def get_trending_tshirts(query=None):
	
	query_sql = ""
	salesrank_threshold = 300000

	if query:
		query_sql = "and lower(asin_metadata.title) like '%%{}%%'".format(query.lower())
		salesrank_threshold = 1000000

	min_last_indexed_date = (datetime.datetime.utcnow() - timedelta(days=2)).isoformat()

	'''
	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, asin_analytics.list_price,
	asin_metadata.title, asin_metadata.brand, asin_metadata.image
	
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	
	WHERE salesrank < {} and last_7d_salesrank < 1000000000
	and asin_analytics.list_price > 0
	and last_7d_salesrank/salesrank >= 1.2
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	and asin_analytics.last_indexed_date > '{}'
	{}
	ORDER BY last_7d_salesrank/((1+(salesrank/100000))*salesrank) DESC 

	LIMIT 500;
	""".format(salesrank_threshold, min_last_indexed_date, query_sql)
	print(sql)
	'''

	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, asin_analytics.list_price,
	asin_metadata.title, asin_metadata.brand, asin_metadata.image
	
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	
	WHERE salesrank < {} and last_7d_salesrank < 1000000000
	and asin_analytics.list_price > 0
	and last_7d_salesrank/salesrank >= 1.2
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	and asin_analytics.last_indexed_date > '{}'

	{}
	ORDER BY last_7d_salesrank/((1+(salesrank/100000))*salesrank) DESC 

	LIMIT 500;
	""".format(salesrank_threshold, min_last_indexed_date, query_sql)
	print(sql)

	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[6]
		if "no-img-sm" in image:
			continue
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"list_price": row[3],
			"title": row[4],
			"brand": row[5],
			"image": row[6]
		})
	print("processed {} search results".format(len(result)))
	result = sorted(result, key=lambda k: k['salesrank']) 
	return result



@app.route("/product_metadata/<asin>")
@login_required
def product_data(asin):
	snapshots = get_snapshots(asin)
	snapshots = sorted(snapshots, key=lambda k: k['timestamp']) 
	keywords = get_tracked_keywords_for_asin(asin)
	"""
	salesranks = [int(s.get("salesrank") or 0) for s in snapshots]
	list_prices = [float(s.get("list_price") or 0.0) for s in snapshots]
	timestamps = [s.get("timestamp").split('T')[0] for s in snapshots]
	data = {
		"salesranks": salesranks,
		"list_prices": list_prices,
		"timestamps": timestamps
	}
	print(data)
	"""

	cleaned_keywords = []
	keywords = sorted(keywords, key=lambda k: int(k.get("position", 10000)), reverse=False)

	for snapshot in snapshots:
		snapshot["salesrank"] = int(snapshot.get("salesrank") or 0)
		snapshot["list_price"] = float(snapshot.get("list_price") or 0)
		snapshot["timestamp"] = snapshot["timestamp"].split('T')[0].split('-')[1] + "/" + snapshot["timestamp"].split('T')[0].split('-')[2]

	#print("these r snapshots")
	#print(snapshots)
	trademarks = get_trademarks_for_asin(asin)
	#print("these are trademarks")
	#print(trademarks)
	return json.dumps({"snapshots": snapshots, "keywords": keywords, "trademarks": trademarks})

def get_favorite_asins(username):
	return firebase_api.query_objects("merchFavorites/{}".format(username))

def generate_dashboard_data(query):
	trending_tshirts = get_trending_tshirts(query)
	trending_tshirts_last_7d = get_trending_tshirts_last_7d(query)
	#best_sellers = get_bestsellers()
	#best_sellers = []

	trending_tshirt_keywords = get_trending_tshirt_keywords(300, query)
	#best_seller_keywords = get_best_seller_keywords(100, query)
	#best_seller_keywords = []

	#trending_tshirts_escore = get_trending_tshirts_by_metric("escore", query, asc=False)
	#trending_tshirts_weighted_escore_v1 = get_trending_tshirts_by_metric("weighted_escore_v1", query, asc=False)
	#trending_tshirts_weighted_escore_v2 = get_trending_tshirts_by_metric("weighted_escore_v2", query, asc=False)
	#trending_tshirts_streak_score_v1 = get_trending_tshirts_by_metric("streak_score_v1/(salesrank/1000000.0)", query, asc=False)
	trending_tshirts_streak_score_v2 = get_trending_tshirts_by_metric("streak_score_v2/(salesrank/1000000.0)", query, asc=False, filter_zeroes=True)
	#recently_discovered_shirts = get_trending_tshirts_by_metric("discovery_timestamp", query, asc=False)


	favorites_by_asin = get_favorite_asins(current_user.username) or {}

	return {
		"trending_tshirt_keywords": trending_tshirt_keywords,
		#"best_seller_keywords": best_seller_keywords,
		#"trending_tshirt_keywords": [],
		"best_seller_keywords": [],
		"whats_hot_this_week": trending_tshirts,
		"whats_hot_last_7d": trending_tshirts_last_7d,
		#"whats_hot_escore": trending_tshirts_escore,
		#"whats_hot_weighted_escore_v1": trending_tshirts_weighted_escore_v1,
		#"whats_hot_weighted_escore_v2": trending_tshirts_weighted_escore_v2,
		#"whats_hot_streak_score_v1": trending_tshirts_streak_score_v1,
		"whats_hot_streak_score_v2": trending_tshirts_streak_score_v2,
		"recently_discovered_shirts": [],
		#"best_sellers": best_sellers
		"best_sellers": [],
		"favorites_by_asin": favorites_by_asin
	}
@app.route("/dashboard_data/")
@login_required
def dashboard_data():
	"""
	if app.config.get('DEVELOPMENT'):
		return requests.get("merchlab.herokuapp.com/dashboard_data/").content
	"""

	print(current_user.user_details, "here")
	query = None
	data = generate_dashboard_data(query)
	return json.dumps(data)


@app.route("/dashboard/search/", methods=["POST"])
@login_required
def dashboard_search():
	print("dashboard_search")
	print(request.json)
	query = request.json["query"].replace("'", "''")
	data = generate_dashboard_data(query)
	return json.dumps(data)

@app.route('/settings/', methods=["GET"])
def settings():
	return redirect(url_for("user_settings"))

@app.route('/settings/user_settings/', methods=["GET"])
def user_settings():
	user = firebase_api.find_user_by_username(current_user.username)
	return render_template("settings/user_settings.html", user=user)


@app.route('/settings/update/', methods=["POST"])
def update_settings():
	user = firebase_api.find_user_by_username(current_user.username)
	result = firebase_api.update_object_and_get_result("users/" + user["objectId"], request.form.get("name"), request.form.get("value"))
	return json.dumps(result)


@app.route("/settings/update_password/", methods=['GET', 'POST'])
def update_password():
	if request.method == 'POST':
		print(request.form, 'ok')
		old_password = request.form["oldPassword"]
		new_password = request.form["newPassword"]
		user = firebase_api.find_user_by_username(current_user.username)
		if user["password"] != hash_pass(old_password):
			return json.dumps({"status": "failure", "error": "Old password did not match with our records."})
		firebase_api.update_object("users/" + user["objectId"],"password", hash_pass(new_password))
		return json.dumps({"status": "success"})

	return render_template("update_password.html")

@login_manager.user_loader
def load_user(userid):
	"""
	Flask-Login user_loader callback.
	The user_loader function asks this function to get a User Object or return 
	None based on the userid.
	The userid was stored in the session environment by Flask-Login.  
	user_loader stores the returned User object in current_user during every 
	flask request. 
	"""
	return models.User.get(userid)

@app.route('/research/', methods=["GET"])
def inventory_v2():
	userId = current_user.username

	userDetails = firebase_api.find_user_by_username(userId)
	if "printerData" in userDetails:
		printerData = userDetails["printerData"]
	else:
		printerData = {}
	return render_template("listings_v3.html")


@app.route('/recent_searches/merch_researcher/', methods=["GET"])
def get_recent_searches():
	username = current_user.username
	sql = """
	SELECT
	query_type, timestamp, query, number_of_merch_shirts_found, average_salesrank, lowest_salesrank,
	bottom_tenth_percentile_salesrank, average_list_price, lowest_price, highest_price,
	best_product_image, best_product_title, best_product_brand

	FROM user_query
	WHERE username='{}'
	AND query_type='merch_researcher'
	ORDER BY timestamp DESC
	LIMIT 100
	""".format(username)

	rows = db.engine.execute(sql);

	entries = []
	for row in rows:
		entry = {
			"query_type": row[0],
			"timestamp": row[1],
			"query": row[2],
			"number_of_merch_shirts_found": row[3],
			"average_salesrank": row[4],
			"lowest_salesrank": row[5],
			"bottom_tenth_percentile_salesrank": row[6],
			"average_list_price": row[7],
			"lowest_price": row[8],
			"highest_price": row[9],
			"best_product_image": row[10],
			"best_product_title": row[11],
			"best_product_brand": row[12]
		}
		entries.append(entry)
	print("processed {} search results".format(len(entries)))
	return json.dumps(entries)



def scrub_negative_queries(query):
	query_split = query.split(' ')
	query_split = [q for q in query_split if len(q) == 0 or q[0] != "-"]
	new_query = " ".join(query_split)
	return new_query

def construct_negative_queries(query):
	query_split = query.split(" ")
	negative_queries = [q[1:] for q in query_split if len(q) > 0 and q[0] == "-"]
	negative_queries_sql = " \n".join(["and asin_metadata.title not like '%%{}%%'".format(q) for q in negative_queries])
	return negative_queries_sql

def execute_query_search(query):
	query_sql = ""
	negative_queries_sql = ""
	scrubbed_query = ""

	if query and query.strip() != "" and len(query) > 1:
		scrubbed_query = scrub_negative_queries(query)
		query_sql = """
		and (
			asin_metadata.title like '%%{}%%'
			or asin_metadata.title like '%%{}%%'
			or asin_metadata.title like '%%{}%%'
		)
		""".format(scrubbed_query, scrubbed_query[0].upper() + scrubbed_query[1:].lower(), scrubbed_query.lower())
		negative_queries_sql = construct_negative_queries(query)
		salesrank_threshold = 2000000
	else:
		salesrank_threshold = 1000000

	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, asin_analytics.list_price,
	asin_metadata.title, asin_metadata.brand, asin_metadata.image, unthrottled_salesrank
	
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	and (asin_metadata.removed IS NULL or asin_metadata.removed = FALSE)

	{}
	{}

	and salesrank < {};
	""".format(query_sql, negative_queries_sql, salesrank_threshold)
	print(sql)	

	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[6]
		if "no-img-sm" in image:
			continue
		image = image.replace("._SL75", "._SL200")
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"list_price": row[3],
			"title": row[4],
			"brand": row[5],
			"image": image,
			"unthrottled_salesrank": row[7]
		})
	result = sorted(result, key=lambda x: x["salesrank"], reverse=False)
	print("processed {} search results".format(len(result)))
	return result

def execute_backup_query_search(query):
	query_sql = ""
	negative_queries_sql = ""
	scrubbed_query = ""


	if query:
		scrubbed_query = scrub_negative_queries(query)
		bigrams = generate_bigrams(scrubbed_query.split(' '))
		#trigrams = generate_trigrams(scrubbed_query.split(' '))
		#print("after", input_list)
		backup_searches = turn_ngrams_into_searches(bigrams)
		backup_searches_sql = ["asin_metadata.title like '%%{}%%'".format(search) for search in backup_searches]
		
		if len(backup_searches_sql) == 0:
			return []
		if len(backup_searches_sql) == 1:
			backup_searches_sql = "and " + backup_searches_sql[0]
		else:
			backup_searches_sql = "and " + backup_searches_sql[0] + " or " + "or \n".join(backup_searches_sql[1:])
		negative_queries_sql = construct_negative_queries(query)
		# let it be 10mil
		salesrank_threshold = 2000000
	else:
		# let it be 1mil
		salesrank_threshold = 1000000

	min_last_indexed_date = (datetime.datetime.utcnow() - timedelta(days=2)).isoformat()

	sql = """
	SELECT asin_analytics.id, asin_analytics.salesrank, asin_analytics.last_7d_salesrank, asin_analytics.list_price,
	asin_metadata.title, asin_metadata.brand, asin_metadata.image, unthrottled_salesrank
	
	FROM asin_analytics 
	INNER JOIN asin_metadata ON asin_analytics.id=asin_metadata.id
	
	and asin_metadata.product_type_name LIKE 'ORCA_SHIRT'
	and (asin_metadata.removed IS NULL or asin_metadata.removed = FALSE)

	{}
	{}

	and salesrank < {};
	""".format(backup_searches_sql, negative_queries_sql, salesrank_threshold)
	print(sql)	
	raw_result = db.engine.execute(sql);
	result = []
	for row in raw_result:
		image = row[6]
		if "no-img-sm" in image:
			continue
		image = image.replace("._SL75", "._SL200")
		result.append({
			"asin": row[0],
			"salesrank": row[1],
			"last_7d_salesrank": row[2],
			"list_price": row[3],
			"title": row[4],
			"brand": row[5],
			"image": image,
			"salesrank": row[7]
		})
	result = sorted(result, key=lambda x: x["salesrank"], reverse=False)
	print("processed {} search results".format(len(result)))
	return result



# Endpoint for searching Merch Researcher.
@app.route('/keyword_search/', methods=["POST"])
def keyword_search():
	userId = current_user.username
	query = request.form.get("query")
	print("executing main query")
	result = execute_query_search(query)
	print("finished main query")
	if len(result) == 0:
		print("executing backup query")
		result = execute_backup_query_search(query)
		print("finished backup query")

	print("constructing keywords from titles")
	titles = [r.get("title") for r in result if r.get("title")]
	keywords = get_keywords_from_titles(500, titles)
	print("finished constructing keywords from titles")

	timestamp = datetime.datetime.utcnow().isoformat()
	
	print("storing user query results")

	if query and query.strip() != "":
		user_query_data = {
			"query_type": "merch_researcher",
			"username": current_user.username,
			"timestamp": timestamp,
			"number_of_merch_shirts_found": len(result),
			"query": query.strip(),
			"average_salesrank": None,
			"lowest_salesrank": None,
			"bottom_tenth_percentile_salesrank": None,
			"average_list_price": None,
			"lowest_price": None,
			"highest_price": None,
			"best_product_image": None,
			"best_product_title": None,
			"best_product_brand": None,
		}

		if len(result) > 0:
			# @TOOD: Make this more complete, lots more summary stats to save and re-display to user
			user_query_data["best_product_image"] = result[0].get("image")
			user_query_data["best_product_title"] = result[0].get("title")
			user_query_data["best_product_brand"] = result[0].get("brand")
			user_query_data["lowest_salesrank"] = result[0].get("salesrank")	


		user_query = models.UserQuery(data=user_query_data)
		db.session.add(user_query)
		try:
			db.session.commit()
			print("committed")
		except Exception as e:
			print(e)
			print("uh oh rollback")
			db.session.rollback()

	print("finished storing user query results")
	print("getting favorites")

	favorites_by_asin = get_favorite_asins(current_user.username) or {}

	print("finished getting favorites")

	#print({"results": result, "keywords": keywords, "favorites_by_asin": favorites_by_asin})
	return json.dumps({"results": result, "keywords": keywords, "favorites_by_asin": favorites_by_asin}, default=alchemyencoder)

if __name__ == "__main__":
	app.run(debug=True)