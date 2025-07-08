import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

# --- CONFIGURATION ---
# The name of the JSON file you downloaded from Google Cloud.
# Make sure this file is in the same folder as this script.
CREDENTIALS_FILE = 'gcp_credentials.json' 

# --- NEW: PASTE THE FULL URL OF YOUR GOOGLE SHEET HERE ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1UXpvz3sP9YBJsv7rSE1GkqG67pNIfKUznkxj8ZMIv-A/edit?gid=0#gid=0"

# --- THE SCRIPT ---

def test_database_connection():
    """
    Connects to your Google Sheet using the credentials file and appends
    a single row of test data to confirm the connection is working.
    """
    print("Attempting to connect to Google Sheets...")

    # --- Input Validation ---
    if "PASTE_THE_FULL_URL" in SHEET_URL:
        print("\n--- ERROR ---")
        print("Please open the test_database.py file and paste the full URL of your Google Sheet into the SHEET_URL variable.")
        return

    try:
        # --- Authentication ---
        scope = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive.file'
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
        client = gspread.authorize(creds)
        
        print(f"Script is using service account email: {creds.service_account_email}")
        print("Authentication successful!")

        # --- Open the sheet and worksheet using the URL ---
        print(f"Attempting to open sheet by URL: {SHEET_URL}")
        sheet = client.open_by_url(SHEET_URL)
        worksheet = sheet.get_worksheet(0)
        print(f"Successfully opened worksheet: '{worksheet.title}'")

        # --- Prepare and write the data ---
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        test_row = [
            "test_id_123",
            current_time,
            "test_keyword",
            "test_source",
            "test_metric",
            100,
            "test_region"
        ]

        print(f"\nAttempting to write the following row to the sheet:\n{test_row}")
        
        worksheet.append_row(test_row)

        print("\n--- SUCCESS! ---")
        print("The test row was successfully added to your Google Sheet.")
        print("Please open your 'Trend_Dashboard_Data' sheet in your browser to verify.")

    except FileNotFoundError:
        print("\n--- ERROR ---")
        print(f"The credentials file was not found. Make sure '{CREDENTIALS_FILE}' is in the same folder as this script.")
    except gspread.exceptions.SpreadsheetNotFound:
        print("\n--- ERROR ---")
        print("The spreadsheet could not be found at the specified URL.")
        print("Please make sure the URL is correct and that you have shared the sheet with the client_email.")
    except Exception as e:
        print(f"\n--- AN UNEXPECTED ERROR OCCURRED ---")
        print(f"Error details: {e}")


# --- RUN THE TEST ---
if __name__ == "__main__":
    test_database_connection()
