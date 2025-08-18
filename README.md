# Financial Results Dashboard (Prototype)

A Streamlit app that helps you:
- Fetch annual/quarterly report PDFs by URL (or upload a PDF manually).
- Extract financial tables (Balance Sheet, P&L, Cash Flow) and Notes to Accounts (basic text capture).
- Preview extracted tables in the app.
- Export everything to a clean Excel workbook for deeper analysis.

> This is a prototype: fetching from NSE/BSE/company IR pages is provided as **stubs** you can extend with your API keys or scraping logic if permitted.

## Quick start

```bash
# 1) Create and activate virtual env (example on Windows PowerShell)
python -m venv .venv
.venv\Scripts\activate

# On macOS/Linux:
python3 -m venv .venv
source .venv/bin/activate

# 2) Install dependencies
pip install -r requirements.txt

# 3) Run the app
streamlit run app.py
```

## How it works (prototype)
- **Upload annual report PDF** or paste a **direct PDF URL**.
- The app uses `pdfplumber` to scan each page, pull tables and nearby headings.
- Heuristics look for keywords like “Balance Sheet”, “Statement of Profit and Loss”, “Cash Flow” to tag tables.
- Notes to Accounts are captured as raw text from pages that include “Notes” or “Significant accounting policies”.
- You can export results to Excel with one click.

## Extend to live fetching
- Implement the functions inside `fetchers/filings.py` to hit NSE/BSE/SEBI endpoints or IR pages.
- Respect robots.txt, site terms, and legal considerations when scraping.
- Consider scheduling (e.g., GitHub Actions/cron) to keep your local DB up-to-date.
