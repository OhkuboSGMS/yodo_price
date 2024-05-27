import os
from typing import Optional

from google.cloud import storage
from google.cloud.storage import Bucket
from google.oauth2.service_account import Credentials


def upload_gcp(
    blob_name: str,
    file_path: str,
    credential_json: Optional[str] = None,
    bucket_name: Optional[str] = None,
):
    credential_json = (
        os.environ["GCP_SERVICE_ACCOUNT"] if not credential_json else credential_json
    )
    bucket_name = os.environ["GCP_BUCKET_NAME"] if not bucket_name else bucket_name

    credential = Credentials.from_service_account_file(credential_json)
    client = storage.Client(credentials=credential)
    bucket: Bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(file_path)
