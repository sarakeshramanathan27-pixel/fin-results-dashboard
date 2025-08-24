import pdfplumber
import pandas as pd
import re

def extract_from_pdf(pdf_path):
    """
    Extract financial data from PDF using pdfplumber.
    Returns a dictionary with extracted tables and text.
    """
    try:
        extracted_data = {
            'balance_sheet': [],
            'profit_loss': [],
            'cash_flow': [],
            'notes': []
        }
        
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages):
                # Extract text
                text = page.extract_text() or ""
                
                # Extract tables
                tables = page.extract_tables()
                
                # Basic heuristics to categorize content
                text_lower = text.lower()
                
                if any(keyword in text_lower for keyword in ['balance sheet', 'statement of financial position']):
                    if tables:
                        extracted_data['balance_sheet'].extend(tables)
                
                elif any(keyword in text_lower for keyword in ['profit and loss', 'statement of profit', 'income statement']):
                    if tables:
                        extracted_data['profit_loss'].extend(tables)
                
                elif any(keyword in text_lower for keyword in ['cash flow', 'statement of cash']):
                    if tables:
                        extracted_data['cash_flow'].extend(tables)
                
                elif any(keyword in text_lower for keyword in ['notes', 'significant accounting policies']):
                    extracted_data['notes'].append(text)
        
        return extracted_data
        
    except Exception as e:
        print(f"Error extracting from PDF: {e}")
        return {
            'balance_sheet': [],
            'profit_loss': [],
            'cash_flow': [],
            'notes': []
        }
