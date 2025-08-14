"""
Lightweight MarkItDown-style adapter used by the platform.
Provides a minimal interface to extract text/markdown from common files
without introducing heavy external dependencies.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional


def to_markdown(file_path: Path, mime_hint: Optional[str] = None) -> Dict[str, str]:
	"""
	Convert a file to markdown-ish text.

	Returns a dict with keys:
	  - text: extracted plain/markdown text
	  - mime: detected/assumed mime string
	"""
	p = Path(file_path)
	suffix = p.suffix.lower()

	if suffix in {".md", ".markdown"}:
		return {"text": p.read_text(encoding="utf-8", errors="ignore"), "mime": "text/markdown"}

	if suffix in {".txt", ""}:
		return {"text": p.read_text(encoding="utf-8", errors="ignore"), "mime": "text/plain"}

	if suffix in {".html", ".htm"}:
		try:
			from bs4 import BeautifulSoup  # optional

			html = p.read_text(encoding="utf-8", errors="ignore")
			soup = BeautifulSoup(html, "html.parser")
			return {"text": soup.get_text("\n").strip(), "mime": "text/html"}
		except Exception:
			# Fallback: return raw content
			return {"text": p.read_text(encoding="utf-8", errors="ignore"), "mime": "text/html"}

	if suffix == ".pdf":
		try:
			import PyPDF2  # optional

			text = ""
			with open(p, "rb") as f:
				reader = PyPDF2.PdfReader(f)
				for page in reader.pages:
					try:
						text += (page.extract_text() or "") + "\n"
					except Exception:
						continue
			return {"text": text.strip(), "mime": "application/pdf"}
		except Exception:
			return {"text": "", "mime": "application/pdf"}

	# Default fallback: read as text
	try:
		return {"text": p.read_text(encoding="utf-8", errors="ignore"), "mime": mime_hint or "application/octet-stream"}
	except Exception:
		return {"text": "", "mime": mime_hint or "application/octet-stream"}
