import requests
import tempfile
import subprocess
import os
from markdownify import markdownify as md

def html_url_to_markdown(url: str) -> str:
    """Fetch a webpage and convert it to Markdown."""
    response = requests.get(url)
    response.raise_for_status()
    html = response.text
    return md(html)

def pdf_url_to_markdown(url: str) -> str:
    """Download a PDF, convert to HTML using pdf2htmlEX, then to Markdown."""
    with tempfile.TemporaryDirectory() as tmpdir:
        pdf_path = os.path.join(tmpdir, "input.pdf")
        html_path = os.path.join(tmpdir, "output.html")

        # Download the PDF
        response = requests.get(url)
        response.raise_for_status()
        with open(pdf_path, "wb") as f:
            f.write(response.content)

        # Convert PDF → HTML
        subprocess.run(
            ["pdf2htmlEX", "--quiet", pdf_path, html_path],
            check=True
        )

        # Read and convert HTML to Markdown
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
            return md(html)


from markitdown import MarkItDown
def parse_pdf(url: str):
    md = MarkItDown()
    result = md.convert(url)
    return result.text_content