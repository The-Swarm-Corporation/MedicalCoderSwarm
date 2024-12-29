import os
import tweepy
from dotenv import load_dotenv
from flask import Flask, request, redirect, session
import webbrowser

# Load environment variables
load_dotenv()

# Flask app for OAuth callback
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Twitter credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
CALLBACK_URL = 'http://127.0.0.1:8000/callback'

def get_oauth_handler():
    """Initialize OAuth handler."""
    return tweepy.OAuth1UserHandler(
        TWITTER_API_KEY,
        TWITTER_API_SECRET,
        callback=CALLBACK_URL
    )

@app.route('/')
def start_auth():
    """Start OAuth flow."""
    try:
        # Get OAuth handler
        oauth = get_oauth_handler()
        
        # Get the authorization URL
        authorization_url = oauth.get_authorization_url()
        
        # Store the request token for later use
        session['request_token'] = oauth.request_token
        
        # Open the authorization URL in browser
        webbrowser.open(authorization_url)
        
        return 'Authorization URL opened in browser. Please complete authentication there.'
    except Exception as e:
        return f'Failed to get authorization URL: {str(e)}'

@app.route('/callback')
def callback():
    """Handle OAuth callback."""
    try:
        # Get the request token from session
        request_token = session.get('request_token')
        if not request_token:
            return 'No request token found. Please start authorization again.'

        # Remove request token from session
        del session['request_token']

        # Get OAuth handler
        oauth = get_oauth_handler()
        
        # Get the verifier from the callback parameters
        verifier = request.args.get('oauth_verifier')
        
        # Set the request token
        oauth.request_token = request_token
        
        # Get the access token
        access_token, access_token_secret = oauth.get_access_token(verifier)

        # Save these tokens in environment file
        with open('.env', 'a') as f:
            f.write(f'\nTWITTER_ACCESS_TOKEN={access_token}')
            f.write(f'\nTWITTER_ACCESS_SECRET={access_token_secret}')

        return 'Authentication successful! You can close this window and restart your bot.'
    except Exception as e:
        return f'Failed to get access token: {str(e)}'

def main():
    """Run the OAuth server."""
    print("Starting OAuth flow...")
    print("A browser window will open. Please authenticate there.")
    app.run(host='127.0.0.1', port=8000)

if __name__ == '__main__':
    main()