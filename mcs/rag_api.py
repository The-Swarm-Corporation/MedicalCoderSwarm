import os
import requests
from swarms_tools.utils.formatted_string import (
    format_object_to_string,
)


class ChromaQueryClient:
    def __init__(
        self,
        api_key: str = os.getenv("RAG_API_URL"),
        base_url: str = os.getenv("RAG_API_URL"),
    ):
        """
        Initializes the ChromaQueryClient with the API key and base URL.

        :param api_key: The API key for authentication.
        :param base_url: The base URL for the Chroma API.
        """
        self.api_key = api_key
        self.base_url = base_url

    def query(self, query: str, n_results: int, doc_limit: int):
        """
        Sends a POST request to the Chroma API to perform a query.

        :param query: The query string to search for.
        :param n_results: The number of results to return.
        :param doc_limit: The document limit for each result.
        :return: The JSON response from the API.
        """
        url = f"{self.base_url}/query"
        headers = {
            "accept": "application/json",
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
        }
        payload = {
            "query": query,
            "n_results": n_results,
            "doc_limit": doc_limit,
        }

        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            result = format_object_to_string(result)

        return result


# # Example usage
# client = ChromaQueryClient()

# # try:
# #     result = client.query(query="back pain", n_results=5, doc_limit=4)
# #     result = format_object_to_string(result)
# #     print(result)
# # except requests.exceptions.RequestException as e:
# #     print("An error occurred:", e)
