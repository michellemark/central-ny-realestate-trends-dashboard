import os
import sqlite3
import time

import boto3
import pandas as pd
import streamlit as st

from constants import ASSESSMENT_RATIOS_TABLE
from constants import DATA_DIR
from constants import DB_LOCAL_PATH
from constants import NY_PROPERTY_ASSESSMENTS_TABLE
from constants import PROPERTIES_TABLE
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


@st.cache_resource(ttl=3600)
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


@st.cache_resource(ttl=3600)
def get_cny_data_df():
    df = pd.DataFrame()

    # Always download latest data from s3
    download_database_from_s3()

    if os.path.exists(DB_LOCAL_PATH):
        db_conn = None

        try:
            db_conn = sqlite3.connect(DB_LOCAL_PATH)

            # Select from properties and ny_property_assessments adding municipality's residential assessment ratio
            query = f"""
                SELECT
                    p.id,
                    p.county_name,
                    p.school_district_name,
                    p.address_street,
                    p.municipality_name,
                    p.address_state,
                    p.address_zip,
                    nypa.roll_year,
                    nypa.property_category,
                    nypa.property_class_description,
                    nypa.full_market_value,
                    nypa.front,
                    nypa.depth,
                    nypa.assessment_land,
                    nypa.assessment_total,
                    mar.residential_assessment_ratio
                FROM
                    {PROPERTIES_TABLE} p
                INNER JOIN
                    {NY_PROPERTY_ASSESSMENTS_TABLE} nypa ON p.id = nypa.property_id
                LEFT JOIN
                    {ASSESSMENT_RATIOS_TABLE} mar ON p.municipality_code = mar.municipality_code;
            """
            df = pd.read_sql_query(query, db_conn)

            # Optimize Data Types to Reduce Memory Usage
            # Convert numeric columns to smaller, efficient types
            df["id"] = df["id"].astype(str)
            df["roll_year"] = df["roll_year"].astype("int16")
            df["full_market_value"] = df["full_market_value"].astype("float32")
            df["front"] = df["front"].astype("float32")
            df["depth"] = df["depth"].astype("float32")
            df["assessment_land"] = df["assessment_land"].astype("float32")
            df["assessment_total"] = df["assessment_total"].astype("float32")
            df["residential_assessment_ratio"] = df["residential_assessment_ratio"].astype("float32")

            # Convert categorical/text columns to "category" to save memory
            category_cols = [
                "county_name",
                "school_district_name",
                "municipality_name",
                "address_state",
                "property_category",
                "property_class_description"
            ]

            for col in category_cols:
                df[col] = df[col].astype("category")
        except Exception as ex:
            st.write(f"Error reading database: {ex}")
        finally:
            db_conn.close()

    return df


def paginate_dataframe(df, page: int, rows_per_page: int):
    """
    Paginate the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to paginate.
        page (int): The current page (zero-indexed).
        rows_per_page (int): Number of rows per page.

    Returns:
        pd.DataFrame: A subset of the DataFrame for the given page.
    """
    start_row = page * rows_per_page
    end_row = start_row + rows_per_page

    return df.iloc[start_row:end_row]
