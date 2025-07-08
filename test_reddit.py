import praw
import os

# --- IMPORTANT: FILL IN YOUR CREDENTIALS HERE ---
# Find these on your Reddit apps page: https://www.reddit.com/prefs/apps
# It's best practice to use environment variables, but for this test,
# you can paste your credentials directly.

CLIENT_ID = "OEuMiv4xJPjdOysuUvwxCQ"         # This is the string of characters under your app's name.
CLIENT_SECRET = "aB6P970ZY9kNkENOWp5-f1XbyY-wzQ" # This is the string next to the word "secret".
USER_AGENT = "TrendAnalyzer by u/Comfortable_State851" # Replace with your Reddit username
REDDIT_USERNAME = "Comfortable_State851"        # Your Reddit username
REDDIT_PASSWORD = "GodForbid2025!"        # Your Reddit password

# --- THE SCRIPT ---

def test_reddit_connection():
    """
    Connects to the Reddit API using your credentials and fetches the top 5
    posts from the r/fashion subreddit to confirm the connection is working.
    """
    print("Attempting to connect to Reddit...")
    
    # --- Input Validation ---
    # Check if the user has replaced the placeholder credentials.
    if "PASTE_YOUR" in CLIENT_ID or "PASTE_YOUR" in CLIENT_SECRET:
        print("\n--- ERROR ---")
        print("Please open the test_reddit.py file and replace the placeholder credentials.")
        print("You need to add your actual Client ID and Client Secret.")
        return # Stop the script if credentials are not filled in.

    try:
        # Initialize the PRAW (Python Reddit API Wrapper) instance
        reddit = praw.Reddit(
            client_id=CLIENT_ID,
            client_secret=CLIENT_SECRET,
            user_agent=USER_AGENT,
            username=REDDIT_USERNAME,
            password=REDDIT_PASSWORD,
            check_for_async=False # Add this line to avoid a common warning
        )

        # This line confirms you have successfully authenticated.
        print(f"Successfully authenticated as: {reddit.user.me()}")

        # Choose a subreddit to test with
        subreddit_name = "fashion"
        subreddit = reddit.subreddit(subreddit_name)

        print(f"\nFetching top 5 'hot' posts from r/{subreddit_name}...")
        print("-" * 30)

        # Get the top 5 posts
        for submission in subreddit.hot(limit=5):
            print(f"TITLE: {submission.title}")
            print(f"SCORE: {submission.score}")
            print(f"URL: {submission.url}")
            print("-" * 30)

    except Exception as e:
        print(f"\n--- AN ERROR OCCURRED ---")
        print(f"Could not connect to Reddit. Please double-check your credentials.")
        print(f"Error details: {e}")

# --- RUN THE TEST ---
if __name__ == "__main__":
    test_reddit_connection()