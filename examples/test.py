import os
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_credentials():
    """Test Twitter credentials step by step."""
    print("\nTesting Twitter API Credentials:")
    print("-" * 40)

    # 1. Load and check credentials existence
    api_key = os.getenv('TWITTER_API_KEY', '').strip()
    api_secret = os.getenv('TWITTER_API_SECRET', '').strip()
    access_token = os.getenv('TWITTER_ACCESS_TOKEN', '').strip()
    access_token_secret = os.getenv('TWITTER_ACCESS_SECRET', '').strip()
    bearer_token = os.getenv('TWITTER_BEARER_TOKEN', '').strip()

    # Check if credentials exist and print masked versions
    credentials = {
        'API Key': api_key,
        'API Secret': api_secret,
        'Access Token': access_token,
        'Access Token Secret': access_token_secret,
        'Bearer Token': bearer_token
    }

    all_present = True
    for name, value in credentials.items():
        if value:
            masked = value[:4] + '*' * (len(value) - 8) + value[-4:]
            print(f"{name}: {masked}")
        else:
            print(f"{name}: MISSING")
            all_present = False

    if not all_present:
        print("\n❌ Some credentials are missing!")
        return

    print("\nTesting individual authentication methods...")

    # 2. Test OAuth 1.0a authentication
    try:
        auth = tweepy.OAuth1UserHandler(
            api_key, 
            api_secret,
            access_token, 
            access_token_secret
        )
        api = tweepy.API(auth)
        api.verify_credentials()
        print("\n✅ OAuth 1.0a Authentication: Successful")
    except Exception as e:
        print(f"\n❌ OAuth 1.0a Authentication Failed: {str(e)}")

    # 3. Test OAuth 2.0 Bearer Token
    try:
        client = tweepy.Client(bearer_token=bearer_token)
        client.get_me()
        print("✅ Bearer Token Authentication: Successful")
    except Exception as e:
        print(f"❌ Bearer Token Authentication Failed: {str(e)}")

    # 4. Test Full v2 Client
    try:
        client = tweepy.Client(
            bearer_token=bearer_token,
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
        me = client.get_me()
        if me.data:
            print(f"✅ Full v2 Client Authentication: Successful")
            print(f"Authenticated as: @{me.data.username}")
    except Exception as e:
        print(f"❌ Full v2 Client Authentication Failed: {str(e)}")

if __name__ == "__main__":
    print("Starting Twitter API Authentication Test")
    test_credentials()