import math

import numpy as np
import plotly.express as px
import streamlit as st

from constants import APP_ICON
from constants import APP_TITLE
from constants import CNY_COUNTY_LIST
from db_utilities import get_cny_data_df
from db_utilities import paginate_dataframe

# Set title and favicon and other default page settings in Browser tab.
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide"
)


# Top of page.
f""" 
# {APP_ICON} {APP_TITLE}

Browse Central New York (CNY) Real Estate data and related statistics from [Open NY](https://data.ny.gov/developers) APIs and 
other free data sources. As you will notice, the data only includes 2024 right now, and some datapoints, such as 
zip codes for properties are often missing. But it's otherwise a great (and did I mention _free_?) source of data.
"""

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

        # Sort data options
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
            ascending=sort_direction == "Descending"
        ).reset_index(drop=True)

        # Pagination Controls
        total_rows = len(filtered_cny_data_df)

        # Select box for rows per page, default 10
        rows_per_page = st.selectbox("Rows per page:", options=[10, 25, 50, 100], index=0)
        total_pages = math.ceil(total_rows / rows_per_page)

        # Keep selected page in session so all controls stay in sync
        if 'selected_page' not in st.session_state:
            st.session_state.selected_page = 1

        # Slider to select page number
        st.session_state.selected_page = st.slider(
            "Page",
            min_value=1,
            max_value=max(total_pages, 1),
            value=st.session_state.selected_page,
            format="Page %d"
        )

        # Get the paginated DataFrame
        paginated_data = paginate_dataframe(sorted_df, st.session_state.selected_page - 1, rows_per_page)

        st.header('CNY Real Estate Data Available', divider='gray')
        # Display paginated data
        st.dataframe(paginated_data)

        # Previous and next page controls for easier navigation when there are a high number of pages
        col_prev, col_info, col_next = st.columns([1, 2, 1])

        with col_prev:
            if st.button("← Previous"):
                if st.session_state.selected_page > 1:
                    st.session_state.selected_page -= 1

        with col_info:
            st.markdown(
                f"<div style='text-align:center'>Page <b>{st.session_state.selected_page}</b> of <b>{total_pages}</b></div>",
                unsafe_allow_html=True)

        with col_next:

            # Use nested columns to align button right
            spacer, next_button_col = st.columns([4, 2])

            with next_button_col:
                if st.button("Next →"):
                    if st.session_state.selected_page < total_pages:
                        st.session_state.selected_page += 1

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
