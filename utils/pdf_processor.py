import pdfplumber
import camelot
import pandas as pd
import tempfile

def process_financial_pdf(uploaded_file, method="auto", chunk_size=50):
    """
    Extract tables and text from a financial PDF.
    Splits the PDF into smaller chunks to handle large files efficiently.
    """
    tables = []
    text_content = []

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        pdf_path = tmp_file.name

    try:
        # Open PDF with pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            total_pages = len(pdf.pages)

            # Process in chunks (e.g. 50 pages at a time)
            for start in range(0, total_pages, chunk_size):
                end = min(start + chunk_size, total_pages)

                # ----------------------------
                # Extract Text
                # ----------------------------
                for page_num in range(start, end):
                    page = pdf.pages[page_num]
                    text = page.extract_text() or ""
                    text_content.append({"page": page_num + 1, "text": text})

                # ----------------------------
                # Extract Tables
                # ----------------------------
                if method in ["auto", "camelot_lattice", "camelot_stream"]:
                    try:
                        flavor = "lattice" if method in ["auto", "camelot_lattice"] else "stream"
                        camelot_tables = camelot.read_pdf(
                            pdf_path,
                            pages=f"{start+1}-{end}",
                            flavor=flavor
                        )
                        for i, t in enumerate(camelot_tables):
                            df = t.df
                            df["source_page"] = start + 1
                            df["table_id"] = i
                            df["extraction_method"] = f"camelot_{flavor}"
                            df["accuracy"] = t.accuracy if hasattr(t, "accuracy") else None
                            tables.append(df)
                    except Exception:
                        if method != "auto":
                            raise

                if method in ["auto", "pdfplumber"]:
                    try:
                        for page_num in range(start, end):
                            page = pdf.pages[page_num]
                            extracted_tables = page.extract_tables()
                            for i, t in enumerate(extracted_tables):
                                df = pd.DataFrame(t)
                                df["source_page"] = page_num + 1
                                df["table_id"] = i
                                df["extraction_method"] = "pdfplumber"
                                df["accuracy"] = None
                                tables.append(df)
                    except Exception:
                        if method != "auto":
                            raise

        return tables, text_content

    except Exception as e:
        raise RuntimeError(f"Error while processing PDF: {str(e)}")
