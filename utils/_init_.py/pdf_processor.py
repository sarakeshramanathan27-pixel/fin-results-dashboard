import streamlit as st
from utils.pdf_processor import process_financial_pdf

st.set_page_config(page_title="Financial Dashboard", page_icon="📊", layout="wide")

def main():
    st.title("📊 Financial Results Dashboard")
    
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    
    if uploaded_file:
        method = st.selectbox("Extraction Method", 
                             ['auto', 'pdfplumber', 'camelot_lattice', 'camelot_stream'])
        
        if st.button("Process PDF"):
            with st.spinner("Processing..."):
                tables, text_content = process_financial_pdf(uploaded_file, method)
                
                if tables:
                    st.success(f"Found {len(tables)} tables!")
                    for i, table in enumerate(tables):
                        st.subheader(f"Table {i+1}")
                        st.dataframe(table)
                else:
                    st.error("No tables found")

if __name__ == "__main__":
    main()
