import firebase_api
import datetime


def assign_va_to_user(username, designer_username, designer_first_name, designer_last_name, rate):
	firebase_api.patch_object(
		"users/" + username + "/virtual_assistants/" + designer_username, 
		{
			"rate": rate,
			"designer_first_name": designer_first_name,
			"designer_last_name": designer_last_name
		}
	)
	firebase_api.patch_object("users/" + designer_username + "/clients/" + username, {rate: rate})

def update_rate(username, designer_username, rate):
	firebase_api.patch_object("users/" + username + "/virtual_assistants/" + designer_username + "/rate", rate)
	firebase_api.patch_object("users/" + designer_username + "/clients/" + username + "/rate", rate)

def unassign_va_from_user(username, designer_username):
	firebase_api.patch_object("users/" + username + "/virtual_assistants/" + designer_username, None)
	firebase_api.patch_object("users/" + designer_username + "/clients/" + username, None)

def get_clients_for_va(designer_username):
	clients = firebase_api.query_objects("users/" + designer_username + "/clients")
	filtered = set()
	for key in clients:
		if filtered[key]:
			filtered.add(key)
	return list(filtered)

def get_vas_for_user(username):
	vas = firebase_api.query_objects("users/" + username + "/virtual_assistants")
	for key in vas:
		vas[key]["designer_username"] = key
	return vas.values()

def get_va_dashboard_data_for_user(username):
	get_breakdown_by_va_for_user(username, is_paid_out=False)


def get_assignment(username, assignment_id):
	assignment = firebase_api.query_objects("assignments/" + username + "/" + assignment_id)
	assignment["id"] = assignment_id
	return assignment

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

def get_commission(username, commission_id):
	return firebase_api.query_objects("commissions/" + commission_id)

def get_commissions_for_user(username, is_paid_out=None, is_approved=None, designer_username=None, start_date=None, end_date=None):
	commissions = firebase_api.query_objects("commissions/" + username) or {}
	filtered = {}
	for key in commissions:
		is_valid = True
		if is_paid_out != None and is_paid_out and not commissions[key].get("paid_out"):
			is_valid = False
		elif is_paid_out != None and not is_paid_out and commissions[key].get("paid_out"):
			is_valid = False
		elif is_approved != None and is_approved and not commissions[key].get("is_approved"):
			is_valid = False
		elif is_approved != None and not is_approved and commissions[key].get("is_approved"):
			is_valid = False
		elif designer_username != None and designer_username != commissions[key].get("designer_username"):
			is_valid = False
		elif start_date != None and start_date > commissions[key].get("created_at"):
			is_valid = False
		elif start_date != None and end_date < commissions[key].get("created_at"):
			is_valid = False

		if is_valid:
			filtered[key] = commissions[key]
	return filtered

def get_breakdown_by_va_for_user(username, is_paid_out=None, is_approved=None, start_date=None, end_date=None):
	commissions = get_commissions_for_user(username, is_paid_out=is_paid_out, is_approved=is_approved, start_date=start_date, end_date=end_date)
	assignments = get_assignments_for_user(username)
	breakdown_by_va = {}
	for key in commissions:
		commission = commissions[key]
		designer_username = commission["designer_username"]
		assignment_id = commission["assignment_id"]
		commission_amount = commission["commission_amount"] or 0
		actual_hours = commission["actual_hours"] or 0
		designs_uploaded = 0
		if assignment_id in assignments:
			assignment = assignments[assignment_id]
			designs_uploaded = len(assignment.get("completed_work", {}))

		if designer_username in breakdown_by_va:
			breakdown = breakdown_by_va[designer_username]
			breakdown["commission_amount"] += commission_amount
			breakdown["actual_hours"] += actual_hours
			breakdown["designs_uploaded"] += designs_uploaded
		else:
			breakdown = {}
			breakdown["commission_amount"] = commission_amount
			breakdown["actual_hours"] = actual_hours
			breakdown["designs_uploaded"] = designs_uploaded
			breakdown_by_va[designer_username] = breakdown

	status_breakdown_by_va = {}
	for assignment_id in assignments:
		assignment = assignments[assignment_id]
		designer_username = assignment.get("designer_username")
		if not designer_username:
			continue

		status = assignment["status"]
		if designer_username not in status_breakdown_by_va:
			status_breakdown_by_va[designer_username] = {status: 0}
		else:
			if status not in status_breakdown_by_va[designer_username]:
				status_breakdown_by_va[designer_username] = 1
			else:
				status_breakdown_by_va[designer_username][status] += 1

	for designer_username in status_breakdown_by_va:
		if designer_username not in breakdown_by_va:
			continue

		status_breakdown = status_breakdown_by_va[designer_username]
		breakdown_by_va[designer_username]["status_breakdown"] = status_breakdown

	return breakdown_by_va

def get_commissions_for_va(designer_username, is_paid_out=None, is_approved=None, start_date=None, end_date=None):
	clients = get_clients_for_va(designer_username)
	all_commisions = []
	for client in clients:
		commissions = get_commissions_for_user(is_paid_out=is_paid_out, is_approved=is_approved, designer_username=designer_username, start_date=start_date, end_date=end_date)
		all_commisions.append(commissions)
	return all_commisions


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

def mark_assignment_as_completed(username, assignment_id, actual_hours):
	assignment = get_assignment(username, assignment_id)
	designer_username = assignment.get("designer_username") or "unassigned" # If user completes it while it is unassigned, then we need to guard against that state
	rate = assignment.get("rate") or 0.0
	data = {
		"status": "completed",
		"actual_hours": actual_hours,
		"completed_on": datetime.datetime.utcnow().isoformat()
	}
	update_assignment(username, assignment_id, data)

	commission_amount = actual_hours * rate
	create_va_commission(username, designer_username, assignment_id, actual_hours, commission_amount)

def mark_assignment_as_in_progress(username, assignment_id):
	update_assignment_progress(username, assignment_id, "in_progress")


def mark_assignment_as_revision_requested(username, assignment_id):
	data = {
		"status": "revision_requested"
	}
	update_assignment(username, assignment_id, data)

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

def add_inspiration_asin_to_assignment(username, assignment_id, asin):
	firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_asins/" + asin, True)

def delete_inspiration_asin_from_assignment(username, assignment_id, asin):
	firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_asins/" + asin, False)

def add_upload_to_assignment(username, assignment_id, upload_uuid):
	firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_uploads/" + upload_uuid, {"s3_url": s3_url})

def delete_upload_from_assignment(username, assignment_id, upload_uuid):
	firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_uploads/" + upload_uuid, None)

def add_completed_work_to_assignment(username, assignment_id, upload_uuid, s3_url):
	return firebase_api.patch_object(
		"assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, 
		{
			"s3_url": s3_url,
			"approved": False
		}
	)

def approve_completed_work(username, assignment_id, upload_uuid):
	return firebase_api.patch_object(
		"assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, 
		{
			"approved": True
		}
	)	

def disapprove_completed_work(username, assignment_id, upload_uuid):
	return firebase_api.patch_object(
		"assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, 
		{
			"approved": False
		}
	)	

def delete_completed_work_from_assignment(username, assignment_id, s3_url):
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, None)
 
def create_va_commission(username, designer_username, assignment_id, actual_hours, commission_amount):
	created_at = datetime.datetime.utcnow().isoformat()
	data = {
		"username": username,
		"designer_username": designer_username,
		"assignment_id": assignment_id,
		"actual_hours": actual_hours,
		"commission_amount": commission_amount,
		"created_at": created_at,
		"approved": True,
		"paid_out": False
	}
	firebase_api.save_object("commissions/" + username, data)

def disapprove_va_commission(username, commission_id):
	firebase_api.patch_object("commissions/" + username + "/approved", False)
