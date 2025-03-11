import math
import os
import sqlite3

import pandas as pd
import streamlit as st

from constants import APP_ICON
from constants import APP_TITLE
from constants import DB_LOCAL_PATH
from constants import OSWEGO_COUNTY_NAME
from db_utilities import download_database_from_s3

# Set title and favicon in Browser tab.
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)


# -----------------------------------------------------------------------------
def get_cny_data_df():
    df = pd.DataFrame()

    if not os.path.exists(DB_LOCAL_PATH):
        download_database_from_s3()

    if os.path.exists(DB_LOCAL_PATH):
        db_conn = None

        try:
            db_conn = sqlite3.connect(DB_LOCAL_PATH)

            # Select all columns from properties and ny_property_assessments joined on property id
            query = """
                SELECT 
                    p.swis_code, p.print_key_code, p.county_name, p.school_district_name, p.address_street, p.municipality_name, p.address_state, p.address_zip, 
                    nypa.roll_year, nypa.property_class_description, nypa.full_market_value, nypa.assessment_land, nypa.assessment_total 
                FROM 
                    properties p
                JOIN 
                    ny_property_assessments nypa 
                ON 
                    p.id = nypa.property_id;
            """
            df = pd.read_sql_query(query, db_conn)
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


# -----------------------------------------------------------------------------
# Draw the actual page

# Set the title that appears at the top of the page.
f""" 
# {APP_ICON} {APP_TITLE}

Browse Central New York (CNY) Real Estate data and related statistics from [Open NY](https://data.ny.gov/developers) APIs and 
other free data sources. As you will notice, the data only includes 2024 right now, and some datapoints, such as 
zip codes for properties are often missing. But it's otherwise a great (and did I mention _free_?) source of data.
"""

# Add some spacing
''
''

cny_data_df = get_cny_data_df()

if not cny_data_df.empty:
    counties = cny_data_df["county_name"].unique()

    if not len(counties):
        st.warning("Select at least one county")

    selected_counties = st.multiselect(
        'Which CNY county would you like to view data for?',
        counties,
        default=OSWEGO_COUNTY_NAME
    )

    ''
    ''
    ''

    # Filter the data
    filtered_cny_data_df = cny_data_df[(cny_data_df['county_name'].isin(selected_counties))]

    st.header('CNY Real Estate Data Available', divider='gray')

    ''

    # Pagination Controls
    total_rows = len(filtered_cny_data_df)

    # Select box for rows per page, default 10
    rows_per_page = st.selectbox("Rows per page:", options=[10, 25, 50, 100], index=0)
    total_pages = math.ceil(total_rows / rows_per_page)

    # Slider to select page number
    selected_page = st.slider(
        "Page", min_value=1, max_value=total_pages, value=1, format="Page %d"
    )

    # Get the paginated DataFrame
    paginated_data = paginate_dataframe(filtered_cny_data_df, selected_page - 1, rows_per_page)

    # Display paginated data
    st.dataframe(paginated_data)

    # Show information about the pagination state
    st.write(f"Showing page {selected_page} of {total_pages} ({len(paginated_data)} rows).")
