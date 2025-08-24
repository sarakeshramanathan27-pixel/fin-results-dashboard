import streamlit as st
import sys
import os

# Add the current directory to Python path to import utils
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
    
    # Sidebar for controls
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
    
    # Main content
    if uploaded_file:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 Process PDF", type="primary", use_container_width=True):
                with st.spinner("🔍 Processing PDF... This may take a moment."):
                    try:
                        tables, text_content = process_financial_pdf(uploaded_file, method)
                        
                        if tables:
                            st.success(f"✅ Successfully extracted {len(tables)} tables!")
                            
                            # Create tabs for different views
                            if len(tables) > 1:
                                tabs = st.tabs([f"Table {i+1}" for i in range(len(tables))])
                                
                                for i, (tab, table) in enumerate(zip(tabs, tables)):
                                    with tab:
                                        # Remove metadata columns for display
                                        display_cols = [col for col in table.columns 
                                                      if col not in ['source_page', 'table_id', 'extraction_method', 'accuracy']]
                                        display_table = table[display_cols] if display_cols else table
                                        
                                        st.dataframe(display_table, use_container_width=True)
                                        
                                        # Show metadata
                                        if 'extraction_method' in table.columns:
                                            st.caption(f"Extracted using: {table['extraction_method'].iloc[0]}")
                                        if 'source_page' in table.columns:
                                            st.caption(f"Source page: {table['source_page'].iloc[0]}")
                                        
                                        # Download button
                                        csv = display_table.to_csv(index=False)
                                        st.download_button(
                                            f"📥 Download Table {i+1}",
                                            csv,
                                            f"financial_table_{i+1}.csv",
                                            "text/csv",
                                            key=f"download_{i}"
                                        )
                            else:
                                # Single table
                                table = tables[0]
                                display_cols = [col for col in table.columns 
                                              if col not in ['source_page', 'table_id', 'extraction_method', 'accuracy']]
                                display_table = table[display_cols] if display_cols else table
                                
                                st.dataframe(display_table, use_container_width=True)
                                
                                # Download button
                                csv = display_table.to_csv(index=False)
                                st.download_button(
                                    "📥 Download Table",
                                    csv,
                                    "financial_table.csv",
                                    "text/csv"
                                )
                            
                            # Show text content if available
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
                            st.info("💡 **Try these solutions:**")
                            st.info("• Check if the PDF contains actual tables (not just text)")
                            st.info("• Try a different extraction method")
                            st.info("• Ensure the PDF is not password protected")
                            
                    except Exception as e:
                        st.error(f"❌ Error processing PDF: {str(e)}")
                        st.info("Please try uploading a different PDF file or contact support.")
    
    else:
        # Welcome screen
        st.markdown("""
        ## 🎯 Welcome to Financial Results Dashboard
        
        Extract and analyze financial data from PDF documents with ease!
        
        ### 🚀 Features:
        - **Multiple extraction methods** for different PDF types
        - **Automatic table detection** and data extraction
        - **Clean data export** to CSV format
        - **Text content viewing** alongside tables
        
        ### 📋 How to use:
        1. **Upload** your PDF using the sidebar
        2. **Choose** an extraction method (Auto recommended)
        3. **Click** Process PDF to extract data
        4. **Download** results as CSV files
        
        ---
        *Supports financial statements, annual reports, and any PDF with tabular data*
        """)

if __name__ == "__main__":
    main()
