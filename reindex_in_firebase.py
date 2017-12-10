from scrapers.asin_indexer import get_existing_asins
from firebase import firebase
from app import db
import models


db_url = "https://blinding-heat-2796.firebaseio.com/"
firebase = firebase.FirebaseApplication(db_url, authentication=None)


data = {'2017-10-19T07:43:49.943836': {'salesrank': 2170073, 'salesrank_category': 'fashion_display_on_website', 'list_price': 15.99}, '2017-10-21T09:13:32.396168': {'salesrank': 2396789, 'salesrank_category': 'fashion_display_on_website', 'list_price': 15.99}}

firebase.put('/asin_snapshots', name="B073JDDXDY", data=data,
params={'print': 'silent'})



asins = list(get_existing_asins())
for asin in asins:
	snapshots = models.AsinSnapshot.query.filter_by(asin=asin).all()
	data = {}
	for snapshot in snapshots:
		data[snapshot.timestamp] = {
			"salesrank": snapshot.salesrank,
			"salesrank_category": snapshot.salesrank_category,
			"list_price": snapshot.list_price
		}
	print(asin)
	print(data)
	firebase.put('/asin_snapshots', name=asin, data=data,
	params={'print': 'silent'})

