from boto import dynamodb2
from boto.dynamodb2.table import Table
import datetime
import decimal
import boto3
from boto3.dynamodb.conditions import Key
import json
import os

def construct_dynamodb_client():
	REGION = "us-east-1"
	AWS_ACCESS_KEY_ID = 'AKIAJNXO62C54H2EOFUA'
	AWS_SECRET_ACCESS_KEY = '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'

	client = boto3.client(
		'dynamodb',
		aws_access_key_id=AWS_ACCESS_KEY_ID,
		aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
		#aws_session_token=SESSION_TOKEN,
		region_name='us-east-1'
	)

	dynamodb = boto3.resource('dynamodb', region_name='us-east-1', aws_access_key_id=AWS_ACCESS_KEY_ID,
		aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

	return dynamodb

def get_correct_table_name(table_name):
	if (os.environ['APP_SETTINGS'] == "config.DevelopmentConfig"):
		return table_name + "_dev"
	elif (os.environ['APP_SETTINGS'] == "config.StagingConfig"):
		return table_name + "_staging"
	elif (os.environ['APP_SETTINGS'] == "config.ProductionConfig"):
		return table_name

def query_table(table_name, filter_key=None, filter_value=None, client=None):
    """
    Perform a query operation on the table. 
    Can specify filter_key (col name) and its value to be filtered.
    """

    if not client:
    	client = construct_dynamodb_client()
    table = client.Table(table_name)

    if filter_key and filter_value:
        filtering_exp = Key(filter_key).eq(filter_value)
        response = table.query(KeyConditionExpression=filtering_exp)
    else:
        response = table.query()

    return response

def query_range(table_name, filter_key=None, filter_lb=None, filter_ub=None, client=None):
    if not client:
    	client = construct_dynamodb_client()
    """
    Perform a query operation on the table. 
    Can specify filter_key (col name) and its value to be filtered.
    """
    table = client.Table(table_name)

    if filter_key and filter_lb and filter_ub:
        filtering_exp = Key(filter_key).between(filter_lb, filter_ub)
        response = table.query(KeyConditionExpression=filtering_exp)
    else:
        response = table.query()

    return response


class InterchangeableObject(dict):
	def __getattr__(self, name):
		if name in self:
			return self[name]
		else:
			raise AttributeError("No such attribute: " + name)

	def __setattr__(self, name, value):
		self[name] = value

	def __delattr__(self, name):
		if name in self:
			del self[name]
		else:
			raise AttributeError("No such attribute: " + name)

class DynamoDBModel(object):
	"""
	Abstraction:
		1) PK fields, Required Fields, Valid Fields expected in this data structure.
		2) If PK/Required fields are missing during initialization, the init function
		will also throw an AttributeError.
		3) If invalid fields are added to the object, we will throw an AttributeError.

	"""
	def __init__(self, data, primary_key_fields, required_fields, valid_fields):
		self.PRIMARY_KEY_FIELDS = primary_key_fields
		self.REQUIRED_FIELDS = required_fields
		self.VALID_FIELDS = valid_fields
		self.model = InterchangeableObject()

		for field in data:
			# Temporarily turn off field validation
			"""
			if field not in self.VALID_FIELDS:
				raise AttributeError("Invalid field present: " + field)
			"""
			self.model[field] = data[field]

		for field in set(list(self.REQUIRED_FIELDS) + list(self.PRIMARY_KEY_FIELDS)):
			if not self.model.get(field):
				raise AttributeError("Required field missing: " + field)

	def set(self, name, value):
		if name not in self.VALID_FIELDS:
			raise AttributeError("Attempted to add invalid field: " + name)
		if type(value) == str:
			self.model[name] = value.encode('utf-8').strip()
		else:
			self.model[name] = value

	def get(self, name):
		if name not in self.VALID_FIELDS:
			raise AttributeError("Attempted to get invalid field: " + name)
		return self.model[name]

def remove_empty_keys(metadata):
	empty_keys = [k for k,v in metadata.iteritems() if not v or v == '']
	for k in empty_keys:
		del metadata[k]	



class UserUploadJob(DynamoDBModel):
	TABLE_NAME = get_correct_table_name("merchlab_user_upload_job")
	PRIMARY_KEY_FIELDS = set(['upload_uuid'])
	REQUIRED_FIELDS = set(['upload_uuid', 'last_updated_date', 'username', 's3_bucket_name', 's3_filename'])
	# VALID FIELDS CODE IS TURNED OFF CURRENTLY - no validation at all
	VALID_FIELDS = set(['upload_uuid', 'last_updated_date', 'error_message', 'job_status', 'output_metadata', 'username', 's3_bucket_name', 's3_filename'])

	def __init__(self, data):
		super(UserUploadJob, self).__init__(
			data,
			self.PRIMARY_KEY_FIELDS, 
			self.REQUIRED_FIELDS, 
			self.VALID_FIELDS
		)

	def add_to_db(self, client):
		try:
			table = client.Table(self.TABLE_NAME)	
			remove_empty_keys(self.model)
			response = table.put_item(
				Item=self.model
			)
			print(response)
			status_code = response['ResponseMetadata']['HTTPStatusCode']
			return status_code == '200'
		except Exception as e:
			if 'ConditionalCheckFailedException' == e.__class__.__name__:
				# This is ok - this means that this was not found in the database
				return False
			else:
				raise Exception(e)

	def update_error_message(self, client):
		if not self.model.error_message:
			raise Exception("Missing 'error_message' field - won't update error message in DynamoDB")

		if not self.model.last_updated_date:
			raise Exception("Missing 'last_updated_date' field - won't update status in DynamoDB")

		try:
			table = client.Table(self.TABLE_NAME)
			update_expression = """
				set error_message=:error_message, 
					last_updated_date=:last_updated_date
			"""
			response = table.update_item(
			    Key={
			        'upload_uuid': self.model.upload_uuid,
			        'username': self.model.username
			    },
			    UpdateExpression=update_expression,
			    ConditionExpression="upload_uuid = :upload_uuid and username = :username",
			    ExpressionAttributeValues={
			        ':last_updated_date': self.model.last_updated_date,
			        ':error_message': self.model.error_message,
			        ':upload_uuid': self.model.upload_uuid,
			        ':username': self.model.username
			    },
			    ReturnValues="UPDATED_NEW"
			)

			# retry attempts might be useful later - let's just define it here
			retry_attempts = response['ResponseMetadata']['RetryAttempts']
			status_code = response['ResponseMetadata']['HTTPStatusCode']
			return status_code == '200'
		except Exception as e:
			if 'ConditionalCheckFailedException' == e.__class__.__name__:
				# This is ok - this means that this was not found in the database
				return False
			else:
				raise Exception(e)

	def update_job_status(self, client):
		if not self.model.job_status:
			raise Exception("Missing 'job_status' field - won't update status in DynamoDB")

		if not self.model.last_updated_date:
			raise Exception("Missing 'last_updated_date' field - won't update status in DynamoDB")

		try:
			table = client.Table(self.TABLE_NAME)
			update_expression = """
				set job_status = :job_status, 
					last_updated_date = :last_updated_date
			"""
			print(self.model.job_status, self.model.last_updated_date)
			response = table.update_item(
			    Key={
			        'upload_uuid': self.model.upload_uuid,
			        'username': self.model.username
			    },
			    UpdateExpression=update_expression,
			    ConditionExpression="upload_uuid = :upload_uuid and username = :username",
			    ExpressionAttributeValues={
			        ':last_updated_date': self.model.last_updated_date,
			        ':job_status': self.model.job_status,
			        ':upload_uuid': self.model.upload_uuid,
			        ':username': self.model.username
			    },
			    ReturnValues="UPDATED_NEW"
			)

			# retry attempts might be useful later - let's just define it here
			retry_attempts = response['ResponseMetadata']['RetryAttempts']
			status_code = response['ResponseMetadata']['HTTPStatusCode']
			return status_code == '200'
		except Exception as e:
			if 'ConditionalCheckFailedException' == e.__class__.__name__:
				# This is ok - this means that this was not found in the database
				return False
			else:
				raise Exception(e)

	def update_job_output_metadata(self, client):
		if not self.model.output_metadata:
			raise Exception("Missing 'output_metadata' field - won't update output metadata in DynamoDB")

		if not self.model.last_updated_date:
			raise Exception("Missing 'last_updated_date' field - won't update status in DynamoDB")

		print("we're using this outputmetadata", self.model.output_metadata)

		try:
			table = client.Table(self.TABLE_NAME)
			update_expression = """
				set output_metadata=:output_metadata, 
					last_updated_date=:last_updated_date
			"""
			response = table.update_item(
			    Key={
			        'upload_uuid': self.model.upload_uuid,
			        'username': self.model.username
			    },
			    UpdateExpression=update_expression,
			    ConditionExpression="upload_uuid = :upload_uuid and username = :username",
			    ExpressionAttributeValues={
			        ':last_updated_date': self.model.last_updated_date,
			        ':output_metadata': self.model.output_metadata,
			        ':upload_uuid': self.model.upload_uuid,
			        ':username': self.model.username
			    },
			    ReturnValues="UPDATED_NEW"
			)

			# retry attempts might be useful later - let's just define it here
			retry_attempts = response['ResponseMetadata']['RetryAttempts']
			status_code = response['ResponseMetadata']['HTTPStatusCode']
			return status_code == '200'
		except Exception as e:
			if 'ConditionalCheckFailedException' == e.__class__.__name__:
				# This is ok - this means that this was not found in the database
				return False
			else:
				raise Exception(e)

	@staticmethod
	def get(username, upload_uuid):
		upload_jobs = UserUploadJob.get_uploads_for_username(username)
		for job in upload_jobs:
			if job.model.upload_uuid == upload_uuid:
				return job


	@staticmethod
	def get_uploads_for_username(username):
		jobs = query_table(UserUploadJob.TABLE_NAME, filter_key='username', filter_value=username).get("Items")
		user_upload_jobs = []
		for job in jobs:
			user_upload_job = UserUploadJob(data=job)
			user_upload_jobs.append(user_upload_job)
		return user_upload_jobs


"""
dynamodb = construct_dynamodb_client()
inventory_item = InventoryItemV2({"seller_id": "abc1231515151", "seller_sku": "abc232", "last_updated_date": "2017", "buy_cost": "0.8"})
#response = inventory_item.update_afn_data(client=dynamodb)
#print(response)
inventory_item.add_inventory_item(client=dynamodb)


dynamodb = construct_dynamodb_client()

inventory_item = InventoryItemV2({"seller_id": "abc1231515151", "seller_sku": "abc232", "last_updated_date": "2018"})
inventory_item.set("pending_quantity", 5)
inventory_item.set("quantity", 1)
inventory_item.update_afn_data(client=dynamodb)
"""

