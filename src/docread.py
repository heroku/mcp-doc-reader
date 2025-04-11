import requests
import tempfile
import subprocess
import os
from markdownify import markdownify as md

def html_to_markdown(url: str) -> str:
    """Fetch a webpage and convert it to Markdown."""
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    return md(html)


from markitdown import MarkItDown
def pdf_to_markdown(url: str):
    md = MarkItDown()
    result = md.convert(url)
    return result.text_content

import pdfplumber
import tempfile
import requests
import os

def pdf_to_markdown2(url: str) -> str:
    """Download a PDF from a URL, extract all text + tables, and return Markdown."""
    output = []

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        response = requests.get(url)
        response.raise_for_status()
        tmp_pdf.write(response.content)
        tmp_pdf_path = tmp_pdf.name

    try:
        with pdfplumber.open(tmp_pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                output.append(f"# 📄 Page {page_num}\n")

                # Extract text with formatting
                text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5)
                if text:
                    clean_text = text.strip().replace('\n', '  \n')  # soft line breaks
                    output.append(clean_text)

                # Extract tables as Markdown
                tables = page.extract_tables()
                for table_num, table in enumerate(tables, start=1):
                    output.append(f"\n### Table {table_num}\n")
                    if table:
                        header = [str(cell or "") for cell in table[0]]
                        output.append("| " + " | ".join(header) + " |")
                        output.append("| " + " | ".join("---" for _ in header) + " |")
                        for row in table[1:]:
                            row_text = " | ".join(str(cell or "") for cell in row)
                            output.append(f"| {row_text} |")

                output.append("")  # space between pages

    finally:
        os.unlink(tmp_pdf_path)

    return "\n".join(output)
