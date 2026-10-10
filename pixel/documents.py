from pathlib import Path
import io

MAX_FILE_BYTES=12*1024*1024
ALLOWED={".txt",".md",".csv",".json",".py",".log",".pdf",".docx"}

def extract_text(filename: str, data: bytes) -> str:
    suffix=Path(filename).suffix.lower()
    if suffix not in ALLOWED: raise ValueError("Supported file types: TXT, MD, CSV, JSON, PY, LOG, PDF, DOCX.")
    if len(data)>MAX_FILE_BYTES: raise ValueError("File exceeds 12 MB limit.")
    if suffix==".pdf":
        try: from pypdf import PdfReader
        except ImportError as exc: raise ValueError("PDF support requires: pip install -e '.[documents]'") from exc
        reader=PdfReader(io.BytesIO(data))
        text="\n".join(page.extract_text() or "" for page in reader.pages)
    elif suffix==".docx":
        try: from docx import Document
        except ImportError as exc: raise ValueError("DOCX support requires: pip install -e '.[documents]'") from exc
        doc=Document(io.BytesIO(data)); text="\n".join(p.text for p in doc.paragraphs)
    else:
        text=data.decode("utf-8-sig",errors="replace")
    return text.strip()
