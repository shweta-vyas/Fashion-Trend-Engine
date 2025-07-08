import pandas as pd
from pytrends.request import TrendReq
import time

def fetch_google_trends_data(keywords: list):
    """
    Fetches interest over time and related queries from Google Trends for a given list of keywords.

    Args:
        keywords (list): A list of strings, where each string is a keyword to search.

    Returns:
        pandas.DataFrame: A DataFrame containing the cleaned and structured data,
                          ready to be saved to the database. Returns an empty DataFrame if an error occurs.
    """
    print(f"Fetching Google Trends data for keywords: {keywords}...")
    
    # Create a list to hold all the data we collect
    all_trends_data = []
    
    try:
        pytrends = TrendReq(hl='en-US', tz=360)

        # We process one keyword at a time to get its related queries accurately
        for keyword in keywords:
            print(f"  - Processing '{keyword}'")
            
            # Build the payload for this specific keyword
            pytrends.build_payload([keyword], cat=0, timeframe='today 1-m', geo='', gprop='')
            
            # --- 1. Get Interest Over Time ---
            interest_df = pytrends.interest_over_time()
            if not interest_df.empty:
                # The 'isPartial' column is not needed, so we drop it
                if 'isPartial' in interest_df.columns:
                    interest_df = interest_df.drop(columns=['isPartial'])
                # Rename the column from the keyword to a generic 'value'
                interest_df = interest_df.rename(columns={keyword: 'value'})
                
                # Add the columns needed for our database
                interest_df['trend_keyword'] = keyword
                interest_df['source'] = 'Google Trends'
                interest_df['metric_type'] = 'search_interest'
                interest_df['region'] = 'global' # Google interest is global by default
                
                # Reset the index to turn the 'date' from an index into a column
                interest_df = interest_df.reset_index()
                
                all_trends_data.append(interest_df)

            # --- 2. Get Related Queries (with improved error handling) ---
            try:
                related_queries = pytrends.related_queries()
                # Check if the keyword has related queries data
                if keyword in related_queries and related_queries[keyword]:
                    # Check for 'top' queries
                    if 'top' in related_queries[keyword] and not related_queries[keyword]['top'].empty:
                        top_df = related_queries[keyword]['top']
                        # Process this data if needed... for now, we'll just print it
                        # print(f"    Top related queries for {keyword}:\n{top_df}")
                    
                    # Check for 'rising' queries
                    if 'rising' in related_queries[keyword] and not related_queries[keyword]['rising'].empty:
                        rising_df = related_queries[keyword]['rising']
                        # print(f"    Rising related queries for {keyword}:\n{rising_df}")
            except Exception as e:
                # If fetching related queries fails, print a warning and continue
                print(f"    - Could not fetch related queries for '{keyword}'. Error: {e}")
                pass


            # It's good practice to wait a moment between requests to avoid getting blocked
            time.sleep(1) 

        if not all_trends_data:
            print("No data was collected from Google Trends.")
            return pd.DataFrame()

        # Combine all the dataframes from the list into one big dataframe
        final_df = pd.concat(all_trends_data, ignore_index=True)
        
        # Add a unique ID for each row
        final_df.insert(0, 'id', range(len(final_df)))
        
        # Reorder columns to match our database schema
        final_df = final_df[['id', 'date', 'trend_keyword', 'source', 'metric_type', 'value', 'region']]
        
        print("\nSuccessfully fetched and structured Google Trends data.")
        return final_df

    except Exception as e:
        print(f"An error occurred while fetching Google Trends data: {e}")
        return pd.DataFrame() # Return an empty dataframe on error


# --- Example of how to use this function ---
if __name__ == '__main__':
    fashion_keywords = ["quiet luxury", "gorpcore", "y2k fashion"]
    google_data = fetch_google_trends_data(fashion_keywords)
    
    if not google_data.empty:
        print("\n--- Sample of Final Structured Data ---")
        print(google_data.head()) # Print the first 5 rows
        print("\n--- Data Info ---")
        google_data.info()