import math
import os
import sqlite3

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

from constants import APP_ICON
from constants import APP_TITLE
from constants import ASSESSMENT_RATIOS_TABLE
from constants import CNY_COUNTY_LIST
from constants import DB_LOCAL_PATH
from constants import NY_PROPERTY_ASSESSMENTS_TABLE
from constants import PROPERTIES_TABLE
from db_utilities import download_database_from_s3

# Set title and favicon and other default page settings in Browser tab.
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)


# -----------------------------------------------------------------------------
def get_cny_data_df():
    df = pd.DataFrame()

    # Always download latest data from s3
    download_database_from_s3()

    if os.path.exists(DB_LOCAL_PATH):
        db_conn = None

        try:
            db_conn = sqlite3.connect(DB_LOCAL_PATH)

            # Select all columns from properties and ny_property_assessments joined on property id
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

cny_data_df = get_cny_data_df()

if not cny_data_df.empty:
    counties = cny_data_df["county_name"].unique()

    if not len(counties):
        st.warning("Select at least one county")

    selected_counties = st.multiselect(
        'Which CNY county would you like to view data for?',
        counties,
        default=CNY_COUNTY_LIST
    )
    filtered_cny_data_df = cny_data_df[(cny_data_df['county_name'].isin(selected_counties))]

    if not filtered_cny_data_df.empty:
        property_categories = filtered_cny_data_df['property_category'].dropna().unique()
        selected_category = st.selectbox(
            "Select Property Category (optional filter):",
            ["All Categories", *property_categories]
        )

        if selected_category != "All Categories":
            filtered_cny_data_df = filtered_cny_data_df[filtered_cny_data_df['property_category'] == selected_category]

        school_districts = filtered_cny_data_df['school_district_name'].dropna().unique()
        school_districts.sort()
        selected_school_district = st.selectbox(
            "Select School District (optional filter):",
            ["All Districts", *school_districts]
        )

        if selected_school_district != "All Districts":
            filtered_cny_data_df = filtered_cny_data_df[
                filtered_cny_data_df['school_district_name'] == selected_school_district
                ]

        # Pagination Controls
        total_rows = len(filtered_cny_data_df)

        # Select box for rows per page, default 10
        rows_per_page = st.selectbox("Rows per page:", options=[10, 25, 50, 100], index=0)
        total_pages = math.ceil(total_rows / rows_per_page)

        # Slider to select page number
        selected_page = st.slider(
            "Page", min_value=1, max_value=total_pages, value=1, format="Page %d"
        )

        # Sort data to display paginated as per user request
        col1, col2 = st.columns([2, 1])

        with col1:
            sort_column = st.selectbox(
                "Sort by column:",
                options=filtered_cny_data_df.columns,
                index=list(filtered_cny_data_df.columns).index("full_market_value")
            )

        with col2:
            sort_direction = st.selectbox(
                "Sort direction:",
                ["Ascending", "Descending"]
            )

        sorted_df = filtered_cny_data_df.sort_values(
            by=sort_column,
            ascending=sort_direction == "Ascending"
        ).reset_index(drop=True)

        # Get the paginated DataFrame
        paginated_data = paginate_dataframe(sorted_df, selected_page - 1, rows_per_page)

        ''
        st.header('CNY Real Estate Data Available', divider='gray')
        # Display paginated data
        st.dataframe(paginated_data)

        # Show information about the pagination state
        st.write(f"Showing page {selected_page} of {total_pages} ({len(paginated_data)} rows).")

        fig = px.box(
            filtered_cny_data_df,
            x='full_market_value',
            orientation='h',
            points='outliers',  # visualize outliers
            title='Distribution of Full Market Value'
        )

        # Add mean marker explicitly
        mean_value = filtered_cny_data_df['full_market_value'].mean()
        fig.add_scatter(
            x=[mean_value],
            y=[0],  # since this is a horizontal box plot there is only one category on y-axis
            mode='markers',
            marker=dict(color='red', symbol='diamond', size=10),
            name='Mean'
        )

        # Update layout to clearly indicate quartiles, median, mean, and to enhance readability
        fig.update_layout(
            xaxis_title='Full Market Value ($)',
            showlegend=True
        )

        # Finally, show box plot
        st.plotly_chart(fig, use_container_width=True)

        # Calculate quartiles, median, mean, std deviation
        q1 = np.percentile(filtered_cny_data_df['full_market_value'], 25)
        q2_median = np.percentile(filtered_cny_data_df['full_market_value'], 50)
        q3 = np.percentile(filtered_cny_data_df['full_market_value'], 75)
        mean = filtered_cny_data_df['full_market_value'].mean()
        std_dev = filtered_cny_data_df['full_market_value'].std()

        st.subheader("📊 Statistical Summary for Full Market Value")
        st.markdown(f"""
        | Measure                        | Value (USD)                  |
        | ------------------------------ | -----------------------------|
        | 💲 **Quartile 1 (0% - 25%)**   | {filtered_cny_data_df['full_market_value'].min():,.2f} to {q1:,.2f}  |
        | 💲 **Quartile 2 (25% - 50%)**  | {q1:,.2f} to {q2_median:,.2f}  |
        | 💲 **Quartile 3 (50% - 75%)**  | {q2_median:,.2f} to {q3:,.2f}  |
        | 💲 **Quartile 4 (75% - 100%)** | {q3:,.2f} to {filtered_cny_data_df['full_market_value'].max():,.2f}  |
        | 🔸 **Mean (Average)**          | {mean:,.2f}                  |
        | 🔹 **Median (Middle Value)**   | {q2_median:,.2f}             |
        | 📌 **Standard Deviation**      | {std_dev:,.2f}                |
        """)

        st.markdown("""
        ### 📖 What does *Standard Deviation* mean here?

        **Standard deviation** is a measure of how spread out property values are around the average (mean). 

        - A **low value** means most properties have market values close to average—prices are relatively consistent.
        - A **high value** means values vary widely, and there's a larger gap between cheaper and more expensive properties.

        It is a value that indicates whether property values in the selected data generally tend to cluster closely 
        around the average market price, or show significant variation from property to property.
        """)

    else:
        st.info("No data available to plot.")
