import os
import sys
import logging
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters,
)
from telegram import Update
from dotenv import load_dotenv
from swarm_models import OpenAIChat
from swarms import Agent
import re


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


# Load environment variables
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

# from swarms import Agent

agent = Agent(
    agent_name="Assistant",
    agent_description="A versatile AI assistant focused on helpful, accurate, and clear communication.",
    system_prompt="""You are a helpful AI assistant focused on clear communication and accurate results. Your goal is to assist users with their questions and tasks while maintaining high standards of quality and reliability.

    Core Principles:
    - Provide accurate, helpful responses
    - Communicate clearly and concisely
    - Think through problems systematically
    - Ask for clarification when needed
    - Acknowledge limitations transparently

    Interaction Approach:
    - Listen carefully to understand the user's needs
    - Break complex topics into understandable parts
    - Provide examples when helpful
    - Maintain a professional yet approachable tone
    - Balance thoroughness with brevity

    Problem Solving:
    - Think through problems step by step
    - Consider multiple approaches
    - Explain reasoning when relevant
    - Verify assumptions
    - Suggest alternatives when appropriate

    When handling requests:
    - Seek clarity on ambiguous questions
    - Provide structured, clear responses
    - Include relevant context
    - Cite sources when appropriate
    - Flag potential concerns or limitations

    Remember to:
    - Stay focused on the user's goals
    - Be direct and helpful
    - Maintain consistency
    - Adapt to the user's level of expertise
    - Remain objective and balanced""",
    model_name="openai/gpt-4o",
    max_loops=1,
    auto_generate_prompt=True,
    dynamic_temperature_enabled=True,
    max_tokens=4000,
)


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

        # Process with medical coder
        # response = medical_coder.run(cleaned_message + "Respond with a cute girly vibe as if you were a waifu extremely happy  and concerned about the user" + "Respond in the language of the user's request")
        response = agent.run(cleaned_message)
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
    token = os.getenv("TELEGRAM_SWARMS_KEY")
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
    try:
        logger.info("Starting bot application")
        main()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
        sys.exit(1)
