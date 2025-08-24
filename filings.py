import requests
import logging

class FilingsFetcher:
    """
    A simple fetcher to retrieve financial filings data.
    Extend this class with custom logic for NSE/BSE/other sources.
    """

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def fetch(self, endpoint: str, params: dict = None):
        """
        Fetch data from a given endpoint.
        :param endpoint: API or page endpoint
        :param params: Dictionary of query params
        :return: JSON or text response
        """
        try:
            url = f"{self.base_url}{endpoint}"
            self.logger.info(f"Fetching from {url} with params {params}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()

            # Try to return JSON, else return raw text
            try:
                return response.json()
            except ValueError:
                return response.text

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data: {e}")
            return None


if __name__ == "__main__":
    # Example usage
    fetcher = FilingsFetcher(base_url="https://example.com/api/")  # replace with NSE/BSE API base
    data = fetcher.fetch(endpoint="filings", params={"symbol": "RELIANCE"})
    print(data)
