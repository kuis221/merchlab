import firebase_api
import datetime


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


def add_inspiration_asin_to_assignment(username, assignment_id, asin):
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_asins/" + asin, True)

def delete_inspiration_asin_from_assignment(username, assignment_id, asin):
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_asins/" + asin, False)

def add_upload_to_assignment(username, assignment_id, upload_uuid):
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_uploads/" + upload_uuid, {"s3_url": s3_url})

def delete_upload_from_assignment(username, assignment_id, upload_uuid):
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/inspiration_uploads/" + upload_uuid, None)

def add_completed_work_to_assignment(username, assignment_id, upload_uuid, s3_url, designer_username):
	return firebase_api.patch_object(
		"assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, 
		{
			"s3_url": s3_url,
			"approval_status": "pending",
			"added_by": designer_username,
			"created_at": datetime.datetime.utcnow().isoformat()
		}
	)
	designers = get_vas_for_user(username)
	rate = 0
	for designer in designers:
		if designer["username"] == designer_username:
			rate = designer.get("rate") or 0
			break
	commission_amount = rate
	create_va_commission(username, designer_username, assignment_id, upload_uuid, commission_amount, approval_status="pending")

def approve_completed_work(username, assignment_id, upload_uuid):
	return firebase_api.patch_object(
		"assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, 
		{
			"approval_status": "approved",
			"approved_on": datetime.datetime.utcnow().isoformat()
		}
	)	

def disapprove_completed_work(username, assignment_id, upload_uuid):
	return firebase_api.patch_object(
		"assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, 
		{
			"approval_status": "rejected",
			"disapproved_on": datetime.datetime.utcnow().isoformat()
		}
	)	

def delete_completed_work_from_assignment(username, assignment_id, s3_url):
	return firebase_api.patch_object("assignments/" + username + "/" + assignment_id + "/completed_work/" + upload_uuid, None)
 
def create_va_commission(username, designer_username, assignment_id, upload_uuid, commission_amount, approval_status="pending"):
	created_at = datetime.datetime.utcnow().isoformat()
	data = {
		"username": username,
		"designer_username": designer_username,
		"assignment_id": assignment_id,
		"commission_amount": commission_amount,
		"created_at": created_at,
		"approval_status": approval_status,
		"paid_out": False
	}
	return firebase_api.save_object("commissions/" + username, data)

def disapprove_va_commission(username, commission_id):
	return firebase_api.patch_object("commissions/" + username + "/" + commission_id + "/approved", False)

def assign_payout_id(username, commission_id, payout_id):
	return firebase_api.patch_object("commissions/" + username + "/" + commission_id + "/payout_id", payout_id)

def mark_commission_as_paid_out(username, commission_id):
	return firebase_api.patch_object("commissions/" + username + "/" + commission_id + "/paid_out", True)


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
		elif is_approved != None and is_approved and not commissions[key].get("approved"):
			is_valid = False
		elif is_approved != None and not is_approved and commissions[key].get("approved"):
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

def get_breakdown_by_va_for_user(username, is_paid_out=None, start_date=None, end_date=None):
	vas = get_vas_for_user(username)
	commissions = get_commissions_for_user(username, is_paid_out=is_paid_out, is_approved=None, start_date=start_date, end_date=end_date)
	assignments = get_assignments_dict_for_user(username)
	breakdown_by_va = {}
	for key in commissions:
		commission = commissions[key]
		is_approved = commission.get("approved", False)
		has_payout_id = commission.get("payout_id") != None
		designer_username = commission["designer_username"]
		assignment_id = commission["assignment_id"]
		commission_amount = commission["commission_amount"] or 0

		unapproved_commission_amount = 0
		approved_commission_amount = 0
		commission_amount_with_payout_id = 0
		commission_amount_without_payout_id = 0

		if is_approved:
			approved_commission_amount = commission_amount
		else:
			unapproved_commission_amount = commission_amount

		if has_payout_id:
			commission_amount_with_payout_id = commission_amount
		else:
			commission_amount_without_payout_id = commission_amount

		actual_hours = commission["actual_hours"] or 0
		designs_uploaded = 0
		if assignment_id in assignments:
			assignment = assignments[assignment_id]
			designs_uploaded = len(assignment.get("completed_work", {}))

		if designer_username in breakdown_by_va:
			breakdown = breakdown_by_va[designer_username]
			breakdown["approved_commission_amount"] += approved_commission_amount
			breakdown["unapproved_commission_amount"] += unapproved_commission_amount
			breakdown["commission_amount_with_payout_id"] += commission_amount_with_payout_id
			breakdown["commission_amount_without_payout_id"] += commission_amount_without_payout_id
			breakdown["actual_hours"] += actual_hours
			breakdown["designs_uploaded"] += designs_uploaded
		else:
			breakdown = {}
			breakdown["approved_commission_amount"] = approved_commission_amount
			breakdown["unapproved_commission_amount"] = unapproved_commission_amount
			breakdown["commission_amount_with_payout_id"] = commission_amount_with_payout_id
			breakdown["commission_amount_without_payout_id"] = commission_amount_without_payout_id
			breakdown["actual_hours"] = actual_hours
			breakdown["designs_uploaded"] = designs_uploaded
			breakdown_by_va[designer_username] = breakdown

	print(commission, approved_commission_amount, unapproved_commission_amount, is_approved)


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

	print("status breakdown by va", status_breakdown_by_va)
	designer_usernames = [va["designer_username"] for va in vas]
	for designer_username in designer_usernames:
		status_breakdown = status_breakdown_by_va.get(designer_username) or {}
		if designer_username not in breakdown_by_va:
			breakdown_by_va[designer_username] = {
				"status_breakdown": status_breakdown,
				"approved_commission_amount": 0,
				"pending_commission_amount": 0,
				"actual_hours": 0,
				"designs_uploaded": 0
			}
		else:
			breakdown_by_va[designer_username]["status_breakdown"] = status_breakdown

	return breakdown_by_va

def get_commissions_for_va(designer_username, is_paid_out=None, is_approved=None, start_date=None, end_date=None):
	clients = get_clients_for_va(designer_username)
	all_commisions = []
	for client in clients:
		commissions = get_commissions_for_user(is_paid_out=is_paid_out, is_approved=is_approved, designer_username=designer_username, start_date=start_date, end_date=end_date)
		all_commisions.append(commissions)
	return all_commisions


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

	commission_amount = num_variations * rate
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

def get_payout(username, designer_username, payout_id):
	return firebase_api.query_objects("payouts/" + username + "/" + designer_username + "/" + payout_id)

def generate_payout_and_mark_as_paid(username, designer_username):
	commissions = get_commissions_for_user(username, is_paid_out=False, is_approved=True, designer_username=designer_username)
	included_in_payout = []
	for commission_id in commissions:
		commission = commissions[commission_id]
		if "payout_id" in commission:
			continue
		else:
			commission["id"] = commission_id
			included_in_payout.append(commission)

	total = sum([commission["commission_amount"] for commission in included_in_payout])

	payout = {
		"included_commissions": included_in_payout,
		"total_amount": total,
		"created_at": datetime.datetime.utcnow().isoformat(),
		"paid_out": True
	}

	# @TODO: Double check through all previously generated payouts, to double confirm that commission ids aren't paid out multiple times
	pass

	# Final step: Mark all commissions as associated with a payout already
	result = firebase_api.save_object("payouts/" + username + "/" + designer_username, payout)
	payout_id = result["name"]
	for commission in included_in_payout:
		commission_id = commission["id"]
		assign_payout_id(username, commission_id, payout_id)

	return payout

"""
def mark_payout_as_paid(username, designer_username, payout_id):
	payout = firebase_api.get_payout(username, designer_username, pyout_id)
	commissions = payout["included_commissions"]
	for commission in commissions:
		commission_id = commission["id"]
		mark_commission_as_paid_out(username, commission_id)
	return firebase_api.patch_object(
		"payouts/" + username + "/" + designer_username + "/" + payout_id, 
		{
			"paid_out": True, 
			"paid_on": datetime.datetime.utcnow().isoformat()
		})
"""
