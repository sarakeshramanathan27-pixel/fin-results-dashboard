import streamlit as st
import pandas as pd
import tempfile
import os
from fetchers.filings import fetch_latest_annual_report_url, download_pdf
from parsers.pdf_parser import extract_from_pdf
from exporters.excel_exporter import export_to_excel

def main():
    st.set_page_config(page_title="Financial Results Dashboard", page_icon="📊", layout="wide")
    
    st.title("📊 Financial Results Dashboard (Prototype)")
    st.markdown("Upload a PDF or provide a direct URL to an annual report. Extract tables and export to Excel.")
    
    # Sidebar for input selection
    st.sidebar.header("Choose Input Mode")
    
    input_mode = st.sidebar.radio(
        "Select how you want to provide the annual report:",
        ["Upload PDF", "Paste PDF URL", "Fetch by Symbol (stub)"]
    )
    
    if input_mode == "Upload PDF":
        handle_pdf_upload()
    elif input_mode == "Paste PDF URL":
        handle_pdf_url()
    else:
        handle_symbol_fetch()

def handle_pdf_upload():
    st.subheader("📁 Upload Annual Report PDF")
    
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload an annual report PDF file (max 200MB)"
    )
    
    if uploaded_file is not None:
        with st.spinner("Processing PDF..."):
            try:
                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    tmp_file_path = tmp_file.name
                
                # Extract data
                extracted_data = extract_from_pdf(tmp_file_path)
                
                # Display results
                display_extracted_data(extracted_data)
                
                # Provide download button
                excel_buffer = export_to_excel(extracted_data)
                if excel_buffer:
                    st.download_button(
                        label="📥 Download Excel Report",
                        data=excel_buffer,
                        file_name="financial_report.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                # Clean up
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")

def handle_pdf_url():
    st.subheader("🔗 Paste PDF URL")
    
    pdf_url = st.text_input(
        "Enter direct PDF URL:",
        placeholder="https://example.com/annual-report.pdf"
    )
    
    if st.button("📥 Download and Process PDF") and pdf_url:
        with st.spinner("Downloading and processing PDF..."):
            try:
                # Create temp file for download
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file_path = tmp_file.name
                
                # Download PDF
                if download_pdf(pdf_url, tmp_file_path):
                    # Extract data
                    extracted_data = extract_from_pdf(tmp_file_path)
                    
                    # Display results
                    display_extracted_data(extracted_data)
                    
                    # Provide download button
                    excel_buffer = export_to_excel(extracted_data)
                    if excel_buffer:
                        st.download_button(
                            label="📥 Download Excel Report",
                            data=excel_buffer,
                            file_name="financial_report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                else:
                    st.error("Failed to download PDF from URL")
                
                # Clean up
                os.unlink(tmp_file_path)
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")

def handle_symbol_fetch():
    st.subheader("🔍 Fetch by Symbol (Stub)")
    st.info("This feature is a prototype stub. Implement NSE/BSE API integration in fetchers/filings.py")
    
    symbol = st.text_input("Enter company symbol (e.g., RELIANCE, TCS):")
    
    if st.button("🔍 Fetch Latest Report") and symbol:
        with st.spinner("Fetching latest report..."):
            try:
                # This is a stub - returns None currently
                pdf_url = fetch_latest_annual_report_url(symbol)
                
                if pdf_url:
                    st.success(f"Found report URL: {pdf_url}")
                    # Process similar to URL method
                else:
                    st.warning("No report found. This is a prototype stub - implement the actual fetching logic.")
            
            except Exception as e:
                st.error(f"Error fetching report: {str(e)}")

def display_extracted_data(extracted_data):
    """Display extracted financial data"""
    st.subheader("📈 Extracted Financial Data")
    
    # Create tabs for different financial statements
    tabs = st.tabs(["Balance Sheet", "Profit & Loss", "Cash Flow", "Notes"])
    
    with tabs[0]:
        display_tables("Balance Sheet", extracted_data.get('balance_sheet', []))
    
    with tabs[1]:
        display_tables("Profit & Loss", extracted_data.get('profit_loss', []))
    
    with tabs[2]:
        display_tables("Cash Flow", extracted_data.get('cash_flow', []))
    
    with tabs[3]:
        display_notes(extracted_data.get('notes', []))

def display_tables(statement_type, tables):
    """Display financial tables"""
    if tables:
        st.write(f"Found {len(tables)} table(s) for {statement_type}")
        
        for i, table in enumerate(tables):
            st.write(f"**Table {i+1}:**")
            
            # Convert to DataFrame for better display
            if table:
                try:
                    df = pd.DataFrame(table)
                    st.dataframe(df, use_container_width=True)
                except:
                    # Fallback to raw table display
                    for row in table:
                        st.write(" | ".join([str(cell) if cell else "" for cell in row]))
                    st.divider()
    else:
        st.info(f"No {statement_type} tables found in the PDF")

def display_notes(notes):
    """Display notes to accounts"""
    if notes:
        st.write(f"Found {len(notes)} note section(s)")
        
        for i, note in enumerate(notes):
            with st.expander(f"Note Section {i+1}"):
                st.text(note)
    else:
        st.info("No notes sections found in the PDF")

if __name__ == "__main__":
    main()
