import streamlit as st
import sys
import os
import pandas as pd

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from utils.pdf_processor import process_financial_pdf
except ImportError as e:
    st.error(f"Error importing PDF processor: {e}")
    st.stop()

st.set_page_config(page_title="Financial Dashboard", page_icon="📊", layout="wide")


def main():
    st.title("📊 Financial Results Dashboard")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Document")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload financial statements or reports"
        )

        if uploaded_file:
            st.success("✅ File uploaded!")
            st.info(f"**File:** {uploaded_file.name}")

            st.header("⚙️ Processing Options")
            method = st.selectbox(
                "Extraction Method",
                ['auto', 'pdfplumber', 'camelot_lattice', 'camelot_stream'],
                help="Auto tries multiple methods automatically"
            )

    # Main area
    if uploaded_file:
        col1, col2, col3 = st.columns([1, 2, 1])

        with col2:
            if st.button("🔄 Process PDF", type="primary", use_container_width=True):
                with st.spinner("🔍 Processing PDF... This may take a while for big files."):
                    try:
                        tables, text_content = process_financial_pdf(uploaded_file, method)

                        if tables:
                            st.success(f"✅ Successfully extracted {len(tables)} tables!")

                            # -----------------------------
                            # SPLIT VIEW ON DASHBOARD
                            # -----------------------------
                            tables_per_page = 10  # show 10 tables at a time
                            num_pages = (len(tables) + tables_per_page - 1) // tables_per_page

                            page = st.number_input(
                                "📄 Page of tables to view",
                                min_value=1, max_value=num_pages, value=1, step=1
                            )

                            start_idx = (page - 1) * tables_per_page
                            end_idx = start_idx + tables_per_page
                            tables_to_show = tables[start_idx:end_idx]

                            for i, table in enumerate(tables_to_show, start=start_idx + 1):
                                st.subheader(f"📊 Table {i}")
                                display_cols = [col for col in table.columns
                                                if col not in ['source_page', 'table_id', 'extraction_method', 'accuracy']]
                                display_table = table[display_cols] if display_cols else table
                                st.dataframe(display_table, use_container_width=True)

                            # -----------------------------
                            # EXPORT ALL TABLES TO EXCEL
                            # -----------------------------
                            all_tables = {}
                            for i, table in enumerate(tables, start=1):
                                display_cols = [col for col in table.columns
                                                if col not in ['source_page', 'table_id', 'extraction_method', 'accuracy']]
                                display_table = table[display_cols] if display_cols else table
                                all_tables[f"Table_{i}"] = display_table

                            with pd.ExcelWriter("financial_results.xlsx", engine="openpyxl") as writer:
                                for name, df in all_tables.items():
                                    df.to_excel(writer, sheet_name=name[:30], index=False)

                            with open("financial_results.xlsx", "rb") as f:
                                st.download_button(
                                    "📥 Download All Tables (Excel)",
                                    f,
                                    "financial_results.xlsx",
                                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                )

                            # -----------------------------
                            # SHOW TEXT CONTENT
                            # -----------------------------
                            if text_content:
                                with st.expander("📄 View Extracted Text"):
                                    for content in text_content:
                                        st.subheader(f"Page {content['page']}")
                                        st.text_area(
                                            f"Text from page {content['page']}",
                                            content['text'][:1000] + "..." if len(content['text']) > 1000 else content['text'],
                                            height=200,
                                            key=f"text_{content['page']}"
                                        )

                        else:
                            st.error("❌ No tables could be extracted from this PDF")
                            st.info("💡 Try a different extraction method or check if the PDF has real tables.")

                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {str(e)}")
                        st.info("Please try uploading a different PDF file or contact support.")

    else:
        # Welcome message
        st.markdown("""
        ## 🎯 Welcome to Financial Results Dashboard

        Extract and analyze financial data from PDF documents with ease!

        ### 🚀 Features:
        - Multiple extraction methods for different PDF types
        - Automatic table detection and data extraction
        - Clean data export to Excel format
        - Text content viewing alongside tables

        ### 📋 How to use:
        1. Upload your PDF using the sidebar  
        2. Choose an extraction method (Auto recommended)  
        3. Click Process PDF to extract data  
        4. Download results as Excel  

        ---
        *Supports financial statements, annual reports, and any PDF with tabular data*
        """)


if __name__ == "__main__":
    main()
