import streamlit as st
import tempfile
import os
import pandas as pd

from fetchers.filings import fetch_latest_annual_report_url, download_pdf
from parsers.pdf_parser import extract_from_pdf
from exporters.excel_exporter import export_to_excel

st.set_page_config(page_title="Financial Results Dashboard", layout="wide")

st.title("📊 Financial Results Dashboard (Prototype)")
st.caption("Upload a PDF or provide a direct URL to an annual report. Extract tables and export to Excel.")

with st.sidebar:
    st.header("Input")
    mode = st.radio("Choose input mode", ["Upload PDF", "Paste PDF URL", "Fetch by Symbol (stub)"])

    tmp_dir = tempfile.mkdtemp()
    pdf_path = None
    meta = {}

    if mode == "Upload PDF":
        uploaded = st.file_uploader("Upload Annual Report PDF", type=["pdf"])
        if uploaded is not None:
            pdf_path = os.path.join(tmp_dir, uploaded.name)
            with open(pdf_path, "wb") as f:
                f.write(uploaded.read())

    elif mode == "Paste PDF URL":
        url = st.text_input("Direct PDF URL")
        if url:
            try:
                pdf_path = os.path.join(tmp_dir, "report.pdf")
                download_pdf(url, pdf_path)
                meta["source_url"] = url
            except Exception as e:
                st.error(f"Download failed: {e}")

    else:
        symbol = st.text_input("Symbol", value="TCS")
        exchange = st.selectbox("Exchange", ["NSE", "BSE"])
        if st.button("Fetch Latest (stub)"):
            res = fetch_latest_annual_report_url(symbol, exchange)
            if res is None:
                st.warning("Fetching is a stub. Please paste a direct PDF URL or upload a PDF.")
            else:
                try:
                    pdf_path = os.path.join(tmp_dir, "report.pdf")
                    download_pdf(res.url, pdf_path)
                    meta.update(res.metadata)
                    meta["source_url"] = res.url
                except Exception as e:
                    st.error(f"Download failed: {e}")

if pdf_path is None:
    st.info("➡️ Provide a PDF to begin.")
    st.stop()

st.success("PDF ready. Click **Extract** to parse tables and notes.")
if st.button("Extract"):
    with st.spinner("Parsing PDF..."):
        tables_by_cat, notes_by_page = extract_from_pdf(pdf_path)

    st.session_state["tables_by_cat"] = tables_by_cat
    st.session_state["notes_by_page"] = notes_by_page
    st.success("Extraction complete. Review below.")

if "tables_by_cat" not in st.session_state:
    st.stop()

tables_by_cat = st.session_state["tables_by_cat"]
notes_by_page = st.session_state["notes_by_page"]

# Summary
total_tables = sum(len(v) for v in tables_by_cat.values())
col1, col2, col3, col4 = st.columns(4)
col1.metric("Balance Sheet tables", len(tables_by_cat.get("balance_sheet", [])))
col2.metric("P&L tables", len(tables_by_cat.get("pnl", [])))
col3.metric("Cash Flow tables", len(tables_by_cat.get("cash_flow", [])))
col4.metric("Other tables", len(tables_by_cat.get("other", [])))
st.divider()

# Show tables
for cat, dfs in tables_by_cat.items():
    if not dfs:
        continue
    st.subheader(f"Section: {cat.replace('_',' ').title()}")
    for idx, df in enumerate(dfs, start=1):
        st.markdown(f"**Table {idx}**")
        st.dataframe(df, use_container_width=True)

# Notes
if notes_by_page:
    st.subheader("📝 Notes to Accounts (raw text capture)")
    for k, v in notes_by_page.items():
        with st.expander(f"{k}"):
            st.write(v)

# Export
out_name = st.text_input("Excel filename", value="financials_extracted.xlsx")
if st.button("Export to Excel"):
    out_path = os.path.join(tmp_dir, out_name)
    try:
        final_path = export_to_excel(tables_by_cat, notes_by_page, out_path)
        with open(final_path, "rb") as f:
            st.download_button("Download Excel", data=f, file_name=out_name, mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        st.success("Excel ready.")
    except Exception as e:
        st.error(f"Export failed: {e}")
        import streamlit as st
from filings import fetch_latest_annual_report_url, download_pdf

st.set_page_config(page_title="NSE Financial Results Dashboard", layout="wide")

st.title("📊 NSE Financial Results Dashboard")

# Input box for NSE symbol
symbol = st.text_input("Enter NSE Stock Symbol (e.g., INFY, TCS, RELIANCE):", "")

if st.button("Fetch Annual Report"):
    if symbol.strip() == "":
        st.warning("⚠️ Please enter a valid NSE stock symbol.")
    else:
        with st.spinner("Fetching latest annual report..."):
            report_url = fetch_latest_annual_report_url(symbol.strip().upper())

        if report_url:
            st.success(f"✅ Found Annual Report for {symbol}")
            st.markdown(f"[📄 View Report Online]({report_url})")

            save_path = f"{symbol}_report.pdf"
            file_path = download_pdf(report_url, save_path)

            if file_path:
                with open(file_path, "rb") as pdf_file:
                    st.download_button(
                        label="⬇️ Download Annual Report",
                        data=pdf_file,
                        file_name=f"{symbol}_annual_report.pdf",
                        mime="application/pdf"
                    )
        else:
            st.error(f"❌ No annual report found for {symbol}")

