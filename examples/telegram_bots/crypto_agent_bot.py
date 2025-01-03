import os
import re
from typing import List
from loguru import logger
from swarm_models import OpenAIChat
from swarms import Agent
from cryptoagent.main import CryptoAgent
from swarms.structs.concat import concat_strings
from cryptoagent.prompts import CRYPTO_AGENT_SYS_PROMPT
from dotenv import load_dotenv

load_dotenv()


class CryptoAnalysisRunner:
    def __init__(self):
        """
        Initializes the CryptoAnalysisRunner with necessary configurations and models.
        """
        logger.info("Initializing CryptoAnalysisRunner...")

        # Check if API key is set
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.error(
                "OPENAI_API_KEY environment variable not set."
            )
            raise EnvironmentError(
                "OPENAI_API_KEY environment variable not set."
            )

        # Initialize the OpenAIChat model
        logger.debug("Initializing the OpenAIChat model...")
        self.model = OpenAIChat(
            openai_api_key=self.api_key,
            model_name="gpt-4o-mini",
            temperature=0.1,
        )

        # Initialize the input agent
        logger.debug("Creating the input agent...")
        self.input_agent = Agent(
            agent_name="Crypto-Analysis-Agent",
            system_prompt=CRYPTO_AGENT_SYS_PROMPT,
            llm=self.model,
            max_loops=1,
            autosave=True,
            dashboard=False,
            verbose=True,
            dynamic_temperature_enabled=True,
            saved_state_path="crypto_agent.json",
            user_name="swarms_corp",
            retry_attempts=1,
            context_length=10000,
        )

        # Initialize CryptoAgent
        logger.debug("Initializing the CryptoAgent...")
        self.crypto_analyzer = CryptoAgent(
            agent=self.input_agent, autosave=True
        )

    def extract_coin_ids(self, task: str) -> List[str]:
        """
        Extracts potential coin IDs from the task string using regex.

        Args:
            task (str): Task description containing coin IDs.

        Returns:
            List[str]: List of extracted coin IDs.
        """
        logger.debug(f"Extracting coin IDs from task: {task}")
        # Match words that are likely coin IDs (assumes alphanumeric words not part of common language)
        pattern = r"\b[a-zA-Z0-9]+\b"
        words = re.findall(pattern, task)

        # A hypothetical filter: exclude common words and focus on valid coin IDs
        common_words = {"conduct", "an", "analysis", "on"}
        coin_ids = [
            word.lower()
            for word in words
            if word.lower() not in common_words
        ]

        logger.debug(f"Extracted coin IDs: {coin_ids}")
        return coin_ids

    def clean_task(self, task: str, coin_ids: List[str]) -> str:
        """
        Cleans the task string by removing coin IDs.

        Args:
            task (str): Original task description.
            coin_ids (List[str]): List of coin IDs to remove from the task.

        Returns:
            str: Cleaned task string.
        """
        logger.debug(f"Cleaning task: {task}")
        cleaned_task = task
        for coin_id in coin_ids:
            cleaned_task = re.sub(
                rf"\b{coin_id}\b",
                "",
                cleaned_task,
                flags=re.IGNORECASE,
            ).strip()
        logger.debug(f"Cleaned task: {cleaned_task}")
        return cleaned_task

    def run(self, task: str) -> str:
        """
        Parses the task to extract coin IDs, removes them from the task, and analyzes them individually.

        Args:
            task (str): Task description containing coin IDs to analyze.

        Returns:
            Dict[str, str]: Analysis summaries for each coin ID.

        Raises:
            ValueError: If no coin IDs are found in the task.
        """
        logger.info("Starting the analysis process...")
        logger.debug(f"Received task: {task}")

        # Extract and validate coin IDs
        coin_ids = self.extract_coin_ids(task)
        if not coin_ids:
            logger.error("No coin IDs found in the task.")
            raise ValueError(
                "The task must include at least one coin ID."
            )

        # Clean the task by removing coin IDs
        cleaned_task = self.clean_task(task, coin_ids)

        # Analyze each coin individually and collect results
        results = []
        for coin_id in coin_ids:
            logger.info(f"Analyzing coin: {coin_id}")
            # Pass the cleaned task and the single coin ID to the CryptoAgent
            summary = self.crypto_analyzer.run(
                [coin_id], cleaned_task
            )
            results.append(summary)

        response = concat_strings(results)
        print(response)

        return response


runner = CryptoAnalysisRunner()
