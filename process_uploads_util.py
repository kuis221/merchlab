from dynamodb_models import UserUploadJob, construct_dynamodb_client
import uuid
import datetime
import boto
from boto.s3.key import Key
import csv
import firebase_api
import json
import util

def download_file_from_s3(bucket_name, filename):
	try:
		AWS_ACCESS_KEY_ID = 'AKIAJNXO62C54H2EOFUA'
		AWS_SECRET_ACCESS_KEY = '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'

		conn = boto.connect_s3(AWS_ACCESS_KEY_ID,
		        AWS_SECRET_ACCESS_KEY)

		print 'Downloading %s from Amazon S3 bucket %s' % \
		   (filename, bucket_name)

		bucket = conn.get_bucket(bucket_name)
		k = Key(bucket)
		k.key = filename
		file = k.get_contents_as_string()
		return file
	except Exception as e:
		print("S3 file download didn't work")
		print(e)
		return None


class UploadDataManager:
	def __init__(self, username, upload_uuid):
		self.username = username
		self.upload_uuid = upload_uuid
		self.client = construct_dynamodb_client()
		"""
		self.upload_job = UserUploadJob(data={
			"username": username,
			"upload_uuid": upload_uuid,
			"last_updated_date": datetime.datetime.utcnow().isoformat(),
		})
		"""
		self.upload_job = UserUploadJob.get(username, upload_uuid)

	def mark_job_queued_for_processing(self):
		self.upload_job.model.job_status = "queued_for_processing"
		self.upload_job.update_job_status(self.client)


	def mark_job_started_processing(self):
		self.upload_job.model.job_status = "processing"
		self.upload_job.update_job_status(self.client)

	def mark_job_as_failed(self, error_message=None):
		self.upload_job.model.job_status = "failed"
		self.upload_job.update_job_status(self.client)

		if error_message:
			self.upload_job.model.error_message = error_message
			self.upload_job.update_error_message(self.client)

	def mark_job_as_processed(self, output_metadata={}):
		self.upload_job.model.job_status = "processed"
		self.upload_job.update_job_status(self.client)

		if not output_metadata:
			return

		self.upload_job.model.output_metadata = output_metadata
		self.upload_job.update_job_output_metadata(self.client)

	def download_file_from_s3(self):
		return download_file_from_s3(self.upload_job.model.s3_bucket_name, self.upload_job.model.s3_filename)

	def get_headers(self):
		pass

	def get_rows(self):
		pass

	def get_upload_job_metadata(self):
		username = self.username
		upload_uuid = self.upload_uuid
		job = UserUploadJob.get(username, upload_uuid)
		return job.model

def create_upload_job(username, s3_bucket_name, s3_filename, override_option, status="queued_for_processing"):
	upload_uuid = str(uuid.uuid4())
	timestamp = datetime.datetime.utcnow().isoformat()
	data={
		"upload_uuid": upload_uuid,
		"last_updated_date": timestamp,
		"job_status": status,
		"username": username,
		"s3_bucket_name": s3_bucket_name,
		"s3_filename": s3_filename
	}
	if override_option:
		data["override_option"] = override_option

	job = UserUploadJob(data=data)
	client = construct_dynamodb_client()
	job.add_to_db(client=client)
	return job

def create_upload_job_designer_upload(username, s3_filename, override_option=None, status="uploaded"):
	job = create_upload_job(username, "merchlab-design-upload", s3_filename, override_option=override_option, status=status)
	return job

if __name__ == "__main__":
	pass
