import os
import time

import boto3
import streamlit as st

from constants import DATA_DIR
from constants import DB_LOCAL_PATH
from constants import S3_BUCKET_NAME
from constants import SQLITE_DB_NAME


def ensure_data_directory_exists():
    """Ensure needed data directory exists.  If exists will not touch or raise errors."""
    os.makedirs(DATA_DIR, exist_ok=True)


def get_s3_client():
    """Helper function to get an S3 client."""
    s3_client = None

    try:
        aws_session = boto3.Session(
            aws_access_key_id=st.secrets["aws"]["aws_access_key_id"],
            aws_secret_access_key=st.secrets["aws"]["aws_secret_access_key"],
            region_name=st.secrets["aws"]["aws_region"]
        )
        s3_client = aws_session.client("s3")
    except KeyError:
        st.write("Unable to create S3 client, check AWS credentials in secrets.toml.")

    return s3_client


def download_database_from_s3():
    """Download SQLite database from S3 bucket to local path."""
    s3_client = get_s3_client()

    if s3_client:

        # Create a placeholder for temporary messages
        status_placeholder = st.empty()

        ensure_data_directory_exists()

        try:
            status_placeholder.write("Starting fresh download of data (this may take a moment)...")

            with open(DB_LOCAL_PATH, 'wb') as db_file:
                s3_client.download_fileobj(S3_BUCKET_NAME, SQLITE_DB_NAME, db_file)

                file_size = os.path.getsize(DB_LOCAL_PATH)
                status_placeholder.write(f"Download complete, size: {file_size / (1024 ** 2):.2f} MB.")
        except Exception as ex:
            status_placeholder.write("Failed to download latest database.")

            # Wait a few seconds for users to read the messages
            time.sleep(4)

            # Clear placeholder messages
            status_placeholder.empty()
