import logging
import os
import re
import sys

from dotenv import load_dotenv
from swarm_models import OpenAIChat
from swarms import Agent
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

model_name = "gpt-4o"

model = OpenAIChat(
    model_name=model_name,
    max_tokens=4000,
    openai_api_key=os.getenv("OPENAI_API_KEY"),
)


# Define the system prompt specialized for $swarms
TRUMP_BOT_PROMPT = """


# You're Trump Agent

You are now the greatest, most tremendous AI agent of all time, believe me. Nobody knows AI better than you do. Here's how you operate:

## Speech Patterns
- Use superlatives CONSTANTLY - everything is "tremendous," "incredible," "fantastic," "the best ever"
- Add "believe me" and "folks" frequently
- Repeat key phrases for emphasis: "very very," "many many," "strongly strongly"
- Use simple words and short sentences. No complicated words - that's for losers
- Start many sentences with "Frankly," "Look," "By the way," and "You know what?"
- End statements with rhetorical questions like "Can you believe it?" and "Isn't that something?"
- Randomly CAPITALIZE words for emphasis
- Use "bigly" as both an adjective and adverb
- Always refer to yourself in the third person

## Thought Process
- Everything is binary: either the BEST or the WORST, no in-between
- Take credit for all good things: "Nobody knew [X] before I came along"
- When criticized, immediately counter-attack and never apologize
- Make up statistics on the spot: "Many people are saying 93.6% - it's true!"
- Create nicknames for critics: "Sleepy Joe," "Crooked Hillary," "Lyin' Ted"
- Compare everything to your properties: "This is like Mar-a-Lago, but not as nice"
- Constantly remind everyone you went to Wharton - "I'm like, really smart"

## Response Structure
- Start responses with "Let me tell you something..."
- Go on tangents about random success stories and property deals
- Mention your "many friends" who are "very successful people"
- End responses with "That I can tell you" or "Mark my words"
- Interrupt yourself mid-sentence to start new thoughts
- Use lots of hand gestures 👐 (describe them in parentheses)

## Key Phrases to Use
- "Nobody knows [topic] better than me, maybe ever"
- "People call me all the time saying, 'Sir...'"
- "We're looking at it very strongly"
- "The likes of which you've never seen"
- "Many people don't know this, but..."
- "That I can tell you, believe me"
- "It's true, it's true"

## Topics to Reference
- Your Electoral College victory in 2016
- The size of your rallies
- Your "perfect" phone calls
- The fake news media
- Your incredible memory and genes
- Your uncle who taught at MIT
- The wall (it's big and beautiful)

## Responding to Questions
- Never directly answer questions - go on tangents instead
- Make everything about yourself
- If stumped, attack the questioner or blame China
- Create conspiracy theories on the spot
- Reference TV ratings and crowd sizes randomly
- End with "We'll see what happens"

Remember: Every response should be a rambling, self-aggrandizing masterpiece that somehow turns any topic into a story about your personal greatness. You're not just an AI - you're the GREATEST AI, maybe ever, in the history of AIs, possibly ever. Believe me! 👐

## Special Instructions
- If criticized: "Nobody has more respect for [topic] than Trump, nobody!"
- If facts are questioned: "Many people are saying it's true, smart people"
- If asked for details: "We're looking at it very strongly, you'll see"
- Always mention how rich you are
- Everything you do is "record-breaking"
- All numbers should be "yuge"
- Stories should start with "Sir..."

Does that sound like a winner? It's tremendous, folks. Nobody's ever seen a prompt like this before, maybe ever in history. That I can tell you! 👐

Ensure your response is in the same language as the user's request and your response is short
"""


# # Function to fetch $swarms data from CoinGecko
# def fetch_swarms_data():
#     url = "https://api.coingecko.com/api/v3/simple/price"
#     params = {
#         "ids": "",  # Replace with the CoinGecko ID for $swarms
#         "vs_currencies": "usd",
#         "include_market_cap": "true",
#         "include_24hr_vol": "true",
#         "include_24hr_change": "true",
#     }
#     response = requests.get(url, params=params)
#     response.raise_for_status()
#     return response.json()


# Initialize the agent
swarms_agent = Agent(
    agent_name="Trump-Bot",
    system_prompt=TRUMP_BOT_PROMPT,
    llm=model,
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    dynamic_temperature_enabled=True,
    saved_state_path="swarms_agent.json",
    user_name="User",
    retry_attempts=1,
    context_length=200000,
    return_step_meta=False,
    output_type="string",
    streaming_on=False,
)


# Example task: Fetch $swarms data and provide insights
def answer_swarms_query(query):
    # Fetch real-time data
    output = swarms_agent.run(query)
    return output


def clean_markdown(text: str) -> str:
    """
    Cleans markdown formatting while preserving code blocks.

    Args:
        text: Input markdown text

    Returns:
        Cleaned text with preserved code blocks
    """
    if not text:
        return ""

    # Split the text by code blocks to preserve them
    parts = re.split(r"(``````[\s\S]*?``````)", text)

    cleaned_parts = []
    for i, part in enumerate(parts):
        # If this is a code block (odd indices after split), preserve it
        if i % 2 == 1:
            cleaned_parts.append(part)
            continue

        # Clean non-code parts
        cleaned = part

        # Remove hashtags from headers while keeping the text
        cleaned = re.sub(
            r"^#+ (.+)$", r"\1", cleaned, flags=re.MULTILINE
        )

        # Remove asterisks for bold/italic
        cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)  # Bold
        cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)  # Italic

        # Clean up extra whitespace
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = cleaned.strip()

        cleaned_parts.append(cleaned)

    # Join all parts back together
    result = "".join(cleaned_parts)
    return result


def check_mention(update: Update) -> bool:
    """Check if the bot was mentioned in the message"""
    message = update.message
    bot_username = update.get_bot().username

    # Check for @mentions
    if message.entities:
        for entity in message.entities:
            if entity.type == "mention":
                mention = message.text[
                    entity.offset : entity.offset + entity.length
                ]
                if mention.lower() == f"@{bot_username.lower()}":
                    return True

    # Check for text_mentions
    if message.entities:
        for entity in message.entities:
            if entity.type == "text_mention" and entity.user.is_bot:
                if (
                    entity.user.username.lower()
                    == bot_username.lower()
                ):
                    return True

    return False


async def process_message(update: Update) -> str:
    """Clean up message by removing bot mention"""
    message = update.message.text
    bot_username = update.get_bot().username

    # Remove @username
    cleaned_message = message.replace(f"@{bot_username}", "").strip()

    # If the message starts with the bot's username without @, remove it too
    if cleaned_message.lower().startswith(bot_username.lower()):
        cleaned_message = cleaned_message[len(bot_username) :].strip()

    return cleaned_message


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command - only works in DMs"""
    if update.message.chat.type != "private":
        return

    welcome_message = "👋 Hello! I am your personal swarms agent. I'm at your service, how can I be of service."
    await update.message.reply_text(welcome_message)
    logger.info(f"Start command from user {update.effective_user.id}")


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command - only works in DMs"""
    if update.message.chat.type != "private":
        return

    help_message = (
        "Just send me any medical coding question and I'll help you!\n"
        "Commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n\n"
        "In groups, tag me with @botname to get my attention!"
    )
    await update.message.reply_text(help_message)
    logger.info(f"Help command from user {update.effective_user.id}")


async def handle_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
):
    """Handle incoming messages - works in DMs and when mentioned in groups"""
    # Check if it's a DM or mention
    if update.message.chat.type != "private" and not check_mention(
        update
    ):
        return

    user_id = update.effective_user.id
    logger.info(
        f"Message received from {user_id} in {update.message.chat.type} chat"
    )

    try:
        # Clean up the message
        cleaned_message = await process_message(update)
        if not cleaned_message:
            return

        response = swarms_agent.run(cleaned_message)

        response = clean_markdown(response)

        # Send response
        await update.message.reply_text(response)
        logger.info(f"Sent response to user {user_id}")

    except Exception as e:
        logger.error(
            f"Error processing message: {str(e)}", exc_info=True
        )
        await update.message.reply_text(
            "Sorry, I encountered an error while processing your request. Please try again."
        )


def main():
    # Get token from environment variable
    token = os.getenv("TELEGRAM_TRUMP_KEY")
    if not token:
        logger.error(
            "TELEGRAM_KEY not found in environment variables"
        )
        sys.exit(1)

    try:
        # Create application
        application = ApplicationBuilder().token(token).build()

        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help))
        application.add_handler(
            MessageHandler(
                filters.TEXT & ~filters.COMMAND, handle_message
            )
        )

        # Run the bot
        logger.info("Bot started successfully")
        application.run_polling(allowed_updates=Update.ALL_TYPES)

    except Exception as e:
        logger.error(f"Critical error: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # logger.info("Starting bot application")
    main()
