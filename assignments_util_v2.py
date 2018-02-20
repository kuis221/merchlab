import firebase_api
import datetime
from app import db
import models

def assign_va_to_user(username, designer_username, rate):
	designer_user = firebase_api.find_user_by_username(designer_username)
	first_name, last_name = designer_user.get("first_name"), designer_user.get("last_name")
	firebase_api.patch_object(
		"virtual_assistants/" + username + "/" + designer_username, 
		{
			"rate": rate,
			"designer_first_name": first_name,
			"designer_last_name": last_name,
			"assigned_on": datetime.datetime.utcnow().isoformat()
		}
	)
	firebase_api.patch_object("clients/" + designer_username + "/" + username, 
		{
			"rate": rate,
			"assigned_on": datetime.datetime.utcnow().isoformat()
		}
	)

def update_rate(username, designer_username, rate):
	firebase_api.patch_object("virtual_assistants/" + username + "/" + designer_username + "/rate", rate)
	return firebase_api.patch_object("clients/" + designer_username + "/" + username + "/rate", rate)

def unassign_va_from_user(username, designer_username):
	firebase_api.patch_object("virtual_assistants/" + username + "/" + designer_username, None)
	return firebase_api.patch_object("clients/" + designer_username + "/" + username, None)

def create_assignment(username, assignment_data):
	created_at = datetime.datetime.utcnow().isoformat()
	assignment_data["created_at"] = created_at
	return firebase_api.save_object("assignments/" + username, assignment_data)

def update_assignment(username, assignment_id, assignment_data):
	updated_on = datetime.datetime.utcnow().isoformat()
	assignment_data["updated_on"] = updated_on
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id, assignment_data)

def update_assignment_progress(username, assignment_id, status):
	update_assignment(username, assignment_id, {"status": status})

def mark_assignment_as_completed(username, assignment_id, actual_hours=0):
	assignment = get_assignment(username, assignment_id)
	designer_username = assignment.get("designer_username") or "unassigned" # If user completes it while it is unassigned, then we need to guard against that state
	rate = assignment["rate"]
	num_variations = assignment["num_variations"]
	data = {
		"status": "completed",
		#"actual_hours": actual_hours,
		"completed_on": datetime.datetime.utcnow().isoformat()
	}
	update_assignment(username, assignment_id, data)

def mark_assignment_as_in_progress(username, assignment_id):
	update_assignment_progress(username, assignment_id, "in_progress")

def assign_va_to_assignment(username, assignment_id, designer_username):
	data = {
		"status": "assigned",
		"designer_username": designer_username
	}
	update_assignment(username, assignment_id, data)

def remove_va_from_assignment(username, assignment_id):
	data = {
		"status": "unassigned",
		"designer_username": None
	}
	update_assignment(username, assignment_id, data)

def update_rate(username, assignment_id, new_rate):
	update_assignment(username, assignment_id, {"rate": new_rate})

def update_num_variations(username, assignment_id, num_variations):
	update_assignment(username, assignment_id, {"num_variations": num_variations})

def update_assignment_name(username, assignment_id, assignment_name):
	update_assignment(username, assignment_id, {"assignment_name": assignment_name})

def update_assignment_description(username, assignment_id, assignment_description):
	update_assignment(username, assignment_id, {"assignment_description": assignment_description})

def update_estimated_hours(username, assignment_id, estimated_hours):
	update_assignment(username, assignment_id, {"estimated_hours": estimated_hours})

def get_clients_for_va(designer_username):
	clients = firebase_api.query_objects("clients/" + designer_username) or {}
	for user_id in clients:
		clients[user_id]["username"] = user_id
	return clients.values()

def get_vas_for_user(username):
	vas = firebase_api.query_objects("virtual_assistants/" + username) or {}
	for key in vas:
		vas[key]["designer_username"] = key
	return vas.values()

def get_assignment(username, assignment_id):
	assignment = firebase_api.query_objects("assignments/" + username + "/" + assignment_id)
	assignment["id"] = assignment_id
	return assignment

def get_assignments_dict_for_user(username):
	assignments = firebase_api.query_objects("assignments/" + username) or {}
	return assignments

def get_assignments_for_user(username, status=None, designer_username=None):
	assignments = firebase_api.query_objects("assignments/" + username) or {}
	return filter_assignments(assignments, status, designer_username)

def filter_assignments(assignments, status=None, designer_username=None):
	filtered = {}
	for key in assignments:
		print(assignments[key])
		is_valid = True
		if status and assignments[key].get("status") != status:
			is_valid = False
		elif designer_username and assignments[key].get("designer_username") != designer_username:
			is_valid = False

		print("is valid", is_valid)

		if is_valid:
			filtered[key] = assignments[key]

	items = []
	for key in filtered:
		item = filtered[key]
		item["id"] = key
		items.append(item)

	return items

#########################################################################################################################

def add_created_design_to_assignment(username, designer_username, assignment_id, 
        commission_amount, mockup_s3_path, assets=[]):
	designers = get_vas_for_user(username)
	rate = 0
	for designer in designers:
		if designer["username"] == designer_username:
			rate = designer.get("rate") or 0
			break
	
	commission_amount = rate
	created_at = datetime.datetime.utcnow().isoformat()
	created_design = models.CreatedDesign(username, designer_username, assignment_id, "pending", created_at, 
        created_at, commission_amount, payout_id=None, mockup_s3_path=mockup_s3_path)
	db.session.add(created_design)

	try:
		db.session.commit()
	except Exception as e:
		print("Failed to add created design to assignment: '{}'".format(str(e)))
		return None

	created_design_assets = add_asset_to_created_design(created_design_id, assets)
	return created_design

def add_assets_to_created_design(created_design_id, assets):
	created_design_assets = []
	for asset in assets:
		created_design_asset = models.CreatedDesignAsset(created_design.id, asset.get("s3_path"), asset.get("revision_id"))
		db.session.add(created_design_asset)
		created_design_assets.append(created_design_asset)
	try:
		db.session.commit()
		return created_design_assets
	except Exception as e:
		print("Failed to add asset to created design: '{}'".format(str(e)))
		db.session.rollback()
		return None

def approve_created_design(username, assignment_id, created_design_id):
	created_design = models.CreatedDesign.filter_by(username=usernane, assignment_id=assignment_id, created_design_id=created_design_id).first()
	if not created_design:
		return None

	created_design.approve()
	try:
		db.session.commit()
		return created_design
	except Exception as e:
		print("Failed to add asset to approve created design: '{}'".format(str(e)))		
		return None

def reject_created_design(username, assignment_id, created_design_id):
	created_design = models.CreatedDesign.filter_by(username=usernane, assignment_id=assignment_id, created_design_id=created_design_id).first()
	if not created_design:
		return None

	created_design.reject()
	try:
		db.session.commit()
		return created_design
	except Exception as e:
		print("Failed to add asset to approve created design: '{}'".format(str(e)))		
		return None

def get_breakdown_by_va_for_user(username, is_paid_out=None, start_date=None, end_date=None):
	vas = get_vas_for_user(username)
	assignments = get_assignments_dict_for_user(username)
	breakdown_by_va = {}
	for designer_username in vas.keys():
		summary = models.CreatedDesign.generate_commission_summary(username, designer_username, start_date, end_date)
		breakdown_by_va[designer_username] = summary

	status_breakdown_by_va = {}
	for assignment_id in assignments:
		assignment = assignments[assignment_id]
		designer_username = assignment.get("designer_username")
		if not designer_username:
			continue

		status = assignment["status"]
		if designer_username not in status_breakdown_by_va:
			status_breakdown_by_va[designer_username] = {}

		if status not in status_breakdown_by_va[designer_username]:
			status_breakdown_by_va[designer_username][status] = 1
		else:
			status_breakdown_by_va[designer_username][status] += 1

	designer_usernames = [va["designer_username"] for va in vas]
	for designer_username in designer_usernames:
		status_breakdown = status_breakdown_by_va.get(designer_username) or {}
		breakdown_by_va[designer_username]["status_breakdown"] = status_breakdown

	return breakdown_by_va

def get_payout(username, designer_username, payout_id):
	return models.Payout.query.filter_by(username=username, designer_username=designer_username, id=payout_id)

def generate_payout(username, designer_username):
	payout = models.Payout.generate_payout_for_user(username, designer_username)
	return payout
