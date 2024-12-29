import os
import time
import logging

import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("twitter_bot.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class TwitterBot:
    def __init__(self):
        """Initialize Twitter bot with your mcsswarm app credentials."""
        self.setup_client()

    def setup_client(self):
        """Set up Twitter client with direct API access."""
        try:
            # Initialize v2 client
            self.client = tweepy.Client(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                consumer_key=os.getenv("TWITTER_API_KEY"),
                consumer_secret=os.getenv("TWITTER_API_SECRET"),
                access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
                access_token_secret=os.getenv(
                    "TWITTER_ACCESS_SECRET"
                ),
                wait_on_rate_limit=True,
            )

            # Test connection and get bot info
            self.me = self.client.get_me()
            logger.info(
                f"Successfully connected as @{self.me.data.username}"
            )

            # Start message stream
            self.setup_stream()

        except Exception as e:
            logger.error(f"Error initializing Twitter client: {e}")
            raise

    def setup_stream(self):
        """Set up filtered stream for mentions."""
        try:
            # Initialize stream
            self.stream = tweepy.StreamingClient(
                bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
                wait_on_rate_limit=True,
            )

            # Add stream rules
            self.stream.add_rules(
                tweepy.StreamRule(f"@{self.me.data.username}")
            )
            logger.info("Stream rules added successfully")

        except Exception as e:
            logger.error(f"Error setting up stream: {e}")
            raise

    async def handle_mention(self, tweet):
        """Handle incoming mentions."""
        try:
            logger.info(f"Processing mention: {tweet.text}")

            # Generate response
            response = f"Thanks for reaching out! I received your message: {tweet.text}"

            # Reply to tweet
            self.client.create_tweet(
                text=response, in_reply_to_tweet_id=tweet.id
            )
            logger.info(f"Replied to tweet {tweet.id}")

        except Exception as e:
            logger.error(f"Error handling mention: {e}")

    async def send_dm(self, user_id: str, message: str):
        """Send a direct message."""
        try:
            response = self.client.create_direct_message(
                participant_id=user_id, text=message
            )
            logger.info(f"DM sent to user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error sending DM: {e}")
            return False

    def start_streaming(self):
        """Start listening for mentions."""
        try:
            logger.info("Starting stream...")
            self.stream.filter(
                tweet_fields=["referenced_tweets", "author_id"],
                expansions=["author_id", "referenced_tweets.id"],
            )
        except Exception as e:
            logger.error(f"Stream error: {e}")
            raise


class MessageHandler(tweepy.StreamingClient):
    def __init__(self, bearer_token, bot):
        super().__init__(bearer_token)
        self.bot = bot

    def on_tweet(self, tweet):
        """Handle incoming tweets."""
        try:
            logger.info(f"Received tweet: {tweet.text}")
            if hasattr(tweet, "referenced_tweets"):
                if any(
                    ref.type == "retweet"
                    for ref in tweet.referenced_tweets
                ):
                    return

            self.bot.handle_mention(tweet)
        except Exception as e:
            logger.error(f"Error in stream: {e}")


def run_bot():
    """Run the Twitter bot."""
    try:
        logger.info("Starting Twitter bot...")
        bot = TwitterBot()

        # Start streaming in the background
        bot.start_streaming()

        # Keep the script running
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        logger.info("Bot shutting down...")
        bot.stream.disconnect()
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise


if __name__ == "__main__":
    run_bot()
