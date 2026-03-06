import sys
import subprocess
try:
    from pypdf import PdfReader
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pypdf"])
    from pypdf import PdfReader

try:
    reader = PdfReader("test.pdf")
    text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    with open("pdf_text.txt", "w", encoding="utf-8") as f:
        f.write(text)
    print("PDF extracted successfully.")
except Exception as e:
    print(f"Error: {e}")
