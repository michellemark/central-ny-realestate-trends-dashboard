import os

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
        ensure_data_directory_exists()

        try:
            st.write(f"Starting download of {SQLITE_DB_NAME} (this may take a moment)...")

            with open(DB_LOCAL_PATH, 'wb') as db_file:
                s3_client.download_fileobj(S3_BUCKET_NAME, SQLITE_DB_NAME, db_file)

                file_size = os.path.getsize(DB_LOCAL_PATH)
                if file_size > 0:
                    st.write(f"Download complete, size: {file_size / (1024 ** 2):.2f} MB.")
                else:
                    st.write("Download completed but resulted in 0 bytes file, please check S3 permissions and file availability.")

                st.write(f"Successfully downloaded database from S3.")
        except Exception as ex:
            st.write(f"Failed to download database from S3: {ex}")
