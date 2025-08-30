import streamlit as st
import pandas as pd
import pdfplumber

# Try to import camelot safely
try:
    import camelot
    CAMELOT_AVAILABLE = True
except ImportError:
    CAMELOT_AVAILABLE = False

st.set_page_config(page_title="Financial Dashboard", page_icon="📊", layout="wide")


def process_financial_pdf(uploaded_file, method="auto"):
    tables = []
    text_content = []

    # Always extract text with pdfplumber
    with pdfplumber.open(uploaded_file) as pdf:
        for i, page in enumerate(pdf.pages, start=1):
            text_content.append({"page": i, "text": page.extract_text() or ""})

    # If Camelot is requested but not available → fallback
    if method.startswith("camelot") and not CAMELOT_AVAILABLE:
        method = "pdfplumber"

    # Camelot methods
    if CAMELOT_AVAILABLE and method in ["camelot_lattice", "camelot_stream"]:
        try:
            flavor = "lattice" if method == "camelot_lattice" else "stream"
            camelot_tables = camelot.read_pdf(uploaded_file, pages="all", flavor=flavor)
            for i, t in enumerate(camelot_tables):
                df = t.df
                df["source_page"] = t.page
                df["extraction_method"] = flavor
                tables.append(df)
        except Exception as e:
            st.warning(f"Camelot failed: {e} → falling back to pdfplumber")
            method = "pdfplumber"  # fallback

    # Pdfplumber extraction
    if method in ["pdfplumber", "auto"]:
        with pdfplumber.open(uploaded_file) as pdf:
            for i, page in enumerate(pdf.pages, start=1):
                try:
                    table = page.extract_table()
                    if table:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        df["source_page"] = i
                        df["extraction_method"] = "pdfplumber"
                        tables.append(df)
                except Exception:
                    continue

    return tables, text_content


def main():
    st.title("📊 Financial Results Dashboard")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Document")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
        if uploaded_file:
            st.success("✅ File uploaded!")
            st.info(f"**File:** {uploaded_file.name}")
            method = st.selectbox(
                "Extraction Method",
                ['auto', 'pdfplumber', 'camelot_lattice', 'camelot_stream'],
                help="Auto tries multiple methods automatically"
            )
        else:
            method = None

    if uploaded_file and method:
        if st.button("🔄 Process PDF", type="primary", use_container_width=True):
            with st.spinner("🔍 Processing PDF..."):
                try:
                    tables, text_content = process_financial_pdf(uploaded_file, method)
                    if tables:
                        st.success(f"✅ Extracted {len(tables)} tables")
                        for i, table in enumerate(tables, start=1):
                            st.subheader(f"Table {i}")
                            st.dataframe(table)
                            st.download_button(
                                f"📥 Download Table {i}",
                                table.to_csv(index=False),
                                f"financial_table_{i}.csv",
                                "text/csv",
                                key=f"download_{i}"
                            )
                    else:
                        st.warning("⚠️ No tables detected in PDF")

                    if text_content:
                        with st.expander("📄 View Extracted Text"):
                            for content in text_content:
                                st.subheader(f"Page {content['page']}")
                                st.text_area("", content['text'], height=150, key=f"text_{content['page']}")
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {e}")

    else:
        st.markdown("""
        ## 🎯 Welcome to Financial Results Dashboard

        Upload annual reports or financial statements and extract tables and text.

        ### 🚀 Features:
        - Multiple extraction methods (pdfplumber + camelot)
        - Automatic fallback to pdfplumber if Camelot fails
        - Export tables to CSV
        - View raw text content alongside tables
        """)


if __name__ == "__main__":
    main()
