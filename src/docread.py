import os
import re
import requests
import tempfile
import pdfplumber
from markdownify import markdownify as md

def html_to_markdown(url: str) -> str:
    """Fetch a webpage and convert it to Markdown."""
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    return md(html)



def _linkify(text: str) -> str:
    """Convert URLs to Markdown-style links."""
    return re.sub(r"(https?://\S+)", r"[\1](\1)", text)


def _sanitize_cell(cell: str) -> str:
    """Escape pipe characters so Markdown tables render properly."""
    return (cell or "").replace("|", "\\|")


def _is_likely_heading(text: str) -> bool:
    """Heuristic for whether a line is a heading."""
    return text.isupper() and len(text.split()) < 10


def _try_bold_heading(line: str) -> str:
    """Bold likely headings based on formatting heuristics."""
    if _is_likely_heading(line):
        return f"**{line}**"
    return line


def pdf_to_markdown(url: str) -> str:
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
                output.append(f"# Page {page_num}\n")

                # Extract text with formatting
                text = page.extract_text(x_tolerance=1.5, y_tolerance=1.5)
                if text:
                    lines = text.strip().splitlines()
                    for line in lines:
                        formatted = _try_bold_heading(_linkify(line.strip()))
                        output.append(formatted + "  ")  # soft line break

                # Extract tables as Markdown
                tables = page.extract_tables()
                for table_num, table in enumerate(tables, start=1):
                    output.append(f"\n### Table {table_num}\n")
                    if table:
                        header = [_sanitize_cell(cell) for cell in table[0]]
                        output.append("| " + " | ".join(header) + " |")
                        output.append("| " + " | ".join("---" for _ in header) + " |")
                        for row in table[1:]:
                            row_text = " | ".join(_sanitize_cell(cell) for cell in row)
                            output.append(f"| {row_text} |")

                output.append("")  # blank line between pages

    finally:
        os.unlink(tmp_pdf_path)

    return "\n".join(output)