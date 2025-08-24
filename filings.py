import requests

BASE_URL = "https://www.nseindia.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36"
}

session = requests.Session()
session.headers.update(HEADERS)


def fetch_latest_annual_report_url(symbol: str) -> str:
    """
    Fetch the latest annual report URL for a given NSE listed company.
    """
    try:
        url = f"{BASE_URL}/api/corporates-financial-results?symbol={symbol}"
        resp = session.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if not data or "financialResults" not in data:
            return None

        reports = data["financialResults"]
        if not reports:
            return None

        latest_report = reports[0]  # first = latest
        return latest_report.get("pdfUrl")

    except Exception as e:
        print(f"Error fetching annual report for {symbol}: {e}")
        return None


def download_pdf(url: str, save_path: str = "annual_report.pdf") -> str:
    """
    Download a PDF from a given URL and save it locally.
    """
    try:
        resp = session.get(url, timeout=20)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        return save_path
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None
