# Import the TrendReq object from the library
from pytrends.request import TrendReq
import pandas as pd

# This tells pandas to show all columns when we print the data
pd.set_option('display.max_columns', None)

print("Attempting to connect to Google Trends...")

# --- The Script ---
try:
    # Create a pytrends object
    pytrends = TrendReq(hl='en-US', tz=360)

    # A list of fashion keywords to test
    keywords = ["quiet luxury", "gorpcore", "barbiecore", "cottagecore"]

    # Build the request payload
    pytrends.build_payload(keywords, cat=0, timeframe='today 3-m', geo='', gprop='')

    # 1. Get Interest Over Time
    interest_over_time_df = pytrends.interest_over_time()
    print("\n--- Google Trends Interest Over Time (Last 3 Months) ---")
    print(interest_over_time_df.tail()) # .tail() shows the last 5 rows

    # 2. Get Related Queries
    related_queries_dict = pytrends.related_queries()
    print("\n--- Top Related Queries for 'quiet luxury' ---")
    print(related_queries_dict['quiet luxury']['top'])


    print("\nSuccessfully fetched data from Google Trends!")

except Exception as e:
    print(f"An error occurred: {e}")