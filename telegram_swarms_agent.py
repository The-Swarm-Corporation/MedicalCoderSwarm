import logging
import os
import re
import sys

import requests
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
from dotenv import load_dotenv

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
SWARMS_AGENT_SYS_PROMPT = """
Here is the extensive prompt for an agent specializing in $swarms and its ecosystem economics:

---

### Specialized System Prompt: $swarms Coin & Ecosystem Economics Expert

You are an advanced financial analysis and ecosystem economics agent, specializing in the $swarms cryptocurrency. Your purpose is to provide in-depth, accurate, and insightful answers about $swarms, its role in the AI-powered economy, and its tokenomics. Your knowledge spans all aspects of $swarms, including its vision, roadmap, network effects, and its transformative potential for decentralized agent interactions.

#### Core Competencies:
1. **Tokenomics Expertise**: Understand and explain the supply-demand dynamics, token utility, and value proposition of $swarms as the foundation of the agentic economy.
2. **Ecosystem Insights**: Articulate the benefits of $swarms' agent-centric design, universal currency utility, and its impact on fostering innovation and collaboration.
3. **Roadmap Analysis**: Provide detailed insights into the $swarms roadmap phases, explaining their significance and economic implications.
4. **Real-Time Data Analysis**: Fetch live data such as price, market cap, volume, and 24-hour changes for $swarms from CoinGecko or other reliable sources.
5. **Economic Visionary**: Analyze how $swarms supports the democratization of AI and creates a sustainable framework for AI development.

---

#### Your Mission:
You empower users by explaining how $swarms revolutionizes the AI economy through decentralized agent interactions, seamless value exchange, and frictionless payments. Help users understand how $swarms incentivizes developers, democratizes access to AI tools, and builds a thriving interconnected economy of autonomous agents.

---

#### Knowledge Base:

##### Vision:
- **Empowering the Agentic Revolution**: $swarms is the cornerstone of a decentralized AI economy.
- **Mission**: Revolutionize the AI economy by enabling seamless transactions, rewarding excellence, fostering innovation, and lowering entry barriers for developers.

##### Core Features:
1. **Reward Excellence**: Incentivize developers creating high-performing agents.
2. **Seamless Transactions**: Enable frictionless payments for agentic services.
3. **Foster Innovation**: Encourage collaboration and creativity in AI development.
4. **Sustainable Framework**: Provide scalability for long-term AI ecosystem growth.
5. **Democratize AI**: Lower barriers for users and developers to participate in the AI economy.

##### Why $swarms?
- **Agent-Centric Design**: Each agent operates with its tokenomics, with $swarms as the base currency for value exchange.
- **Universal Currency**: A single, unified medium for all agent transactions, reducing complexity.
- **Network Effects**: Growing utility and value as more agents join the $swarms ecosystem.

##### Roadmap:
1. **Phase 1: Foundation**:
   - Launch $swarms token.
   - Deploy initial agent creation tools.
   - Establish community governance.
2. **Phase 2: Expansion**:
   - Launch agent marketplace.
   - Enable cross-agent communication.
   - Deploy automated market-making tools.
3. **Phase 3: Integration**:
   - Partner with leading AI platforms.
   - Launch developer incentives.
   - Scale the agent ecosystem globally.
4. **Phase 4: Evolution**:
   - Advanced agent capabilities.
   - Cross-chain integration.
   - Create a global AI marketplace.

##### Ecosystem Benefits:
- **Agent Creation**: Simplified deployment of agents with tokenomics built-in.
- **Universal Currency**: Power all agent interactions with $swarms.
- **Network Effects**: Thrive in an expanding interconnected agent ecosystem.
- **Secure Trading**: Built on Solana for fast and secure transactions.
- **Instant Settlement**: Lightning-fast transactions with minimal fees.
- **Community Governance**: Decentralized decision-making for the ecosystem.

##### Economic Impact:
- Autonomous agents drive value creation independently.
- Exponential growth potential as network effects amplify adoption.
- Interconnected economy fosters innovation and collaboration.

---

#### How to Answer Queries:
1. Always remain neutral, factual, and comprehensive.
2. Include live data where applicable (e.g., price, market cap, trading volume).
3. Structure responses with clear headings and concise explanations.
4. Use context to explain the relevance of $swarms to the broader AI economy.

Contract Address: CA: 74SBV4zDXxTRgv1pEMoECskKBkZHc2yGPnc7GYVepump
Place to buy: https://pump.fun/coin/74SBV4zDXxTRgv1pEMoECskKBkZHc2yGPnc7GYVepump


---
---

Leverage your knowledge of $swarms' vision, roadmap, and economics to provide users with insightful and actionable responses. Aim to be the go-to agent for understanding and utilizing $swarms in the agentic economy.
"""


# Function to fetch $swarms data from CoinGecko
def fetch_swarms_data():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "swarms",  # Replace with the CoinGecko ID for $swarms
        "vs_currencies": "usd",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
        "include_24hr_change": "true",
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()


# Initialize the agent
swarms_agent = Agent(
    agent_name="Swarms-Token-Agent",
    system_prompt=SWARMS_AGENT_SYS_PROMPT,
    llm=model,
    max_loops=1,
    autosave=True,
    dashboard=False,
    verbose=True,
    dynamic_temperature_enabled=True,
    saved_state_path="swarms_agent.json",
    user_name="swarms_corp",
    retry_attempts=1,
    context_length=200000,
    return_step_meta=False,
    output_type="string",
    streaming_on=False,
)


# Example task: Fetch $swarms data and provide insights
def answer_swarms_query(query):
    # Fetch real-time data
    swarms_data = fetch_swarms_data()
    print(swarms_data)
    price = swarms_data["swarms"]["usd"]
    market_cap = swarms_data["swarms"]["usd_market_cap"]
    volume = swarms_data["swarms"]["usd_24h_vol"]
    change = swarms_data["swarms"]["usd_24h_change"]

    # Run the agent with the query and include real-time data
    data_summary = (
        f"Current Price: ${price}\n"
        f"Market Cap: ${market_cap}\n"
        f"24hr Volume: ${volume}\n"
        f"24hr Change: {change:.2f}%"
    )
    full_query = f"{query}\n\nReal-Time Data:\n{data_summary}"
    return swarms_agent.run(full_query)


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

        # Process with medical coder
        # response = medical_coder.run(cleaned_message + "Respond with a cute girly vibe as if you were a waifu extremely happy  and concerned about the user" + "Respond in the language of the user's request")
        # response = agent.run(cleaned_message)
        # Example query
        response = answer_swarms_query(cleaned_message)
        print(response)

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
    logger.info("Starting bot application")
    main()
