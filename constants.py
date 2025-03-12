import os


# ******* File paths and names ***********************************
APP_TITLE = "Central New York Real Estate Analytics"
APP_ICON = "👩‍🎓"
CURRENT_FILE_PATH = os.path.abspath(__file__)
PROJECT_ROOT = os.path.dirname(CURRENT_FILE_PATH)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SQLITE_DB_NAME = "cny-real-estate.db"
DB_LOCAL_PATH = os.path.join(DATA_DIR, SQLITE_DB_NAME)
SQLITE_DB_CONFIG_NAME = "cny_real_estate"
S3_BUCKET_NAME = "cny-realestate-data"

# ******* Table names *********************************************
ASSESSMENT_RATIOS_TABLE = "municipality_assessment_ratios"
NY_PROPERTY_ASSESSMENTS_TABLE = "ny_property_assessments"
PROPERTIES_TABLE = "properties"

# ******* Real Estate values **************************************
CAYUGA_COUNTY_NAME = "Cayuga"
CORTLAND_COUNTY_NAME = "Cortland"
MADISON_COUNTY_NAME = "Madison"
ONONDAGA_COUNTY_NAME = "Onondaga"
OSWEGO_COUNTY_NAME = "Oswego"
CNY_COUNTY_LIST = [
    CAYUGA_COUNTY_NAME,
    CORTLAND_COUNTY_NAME,
    MADISON_COUNTY_NAME,
    ONONDAGA_COUNTY_NAME,
    OSWEGO_COUNTY_NAME
]
