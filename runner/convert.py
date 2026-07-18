from pathlib import Path

import markdown
from weasyprint import HTML

_CSS = """
@page { margin: 2cm; }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 13px;
    line-height: 1.65;
    color: #1a1a1a;
    max-width: 100%;
}
h1 { font-size: 22px; border-bottom: 2px solid #0d47a1; padding-bottom: 6px; color: #0d47a1; }
h2 { font-size: 18px; border-bottom: 1px solid #e0e0e0; padding-bottom: 4px; color: #1565c0; margin-top: 28px; }
h3 { font-size: 15px; color: #1976d2; margin-top: 20px; }
h4 { font-size: 13px; color: #424242; }
code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: 12px;
    background: #f5f5f5;
    padding: 2px 5px;
    border-radius: 3px;
}
pre {
    background: #f5f5f5;
    padding: 14px 16px;
    border-radius: 5px;
    overflow-x: auto;
    font-size: 12px;
    border-left: 3px solid #1565c0;
}
pre code { background: none; padding: 0; }
table {
    border-collapse: collapse;
    width: 100%;
    margin: 12px 0;
    font-size: 12px;
}
th {
    background: #1565c0;
    color: #fff;
    padding: 8px 12px;
    text-align: left;
}
td { padding: 7px 12px; border-bottom: 1px solid #e0e0e0; }
tr:nth-child(even) td { background: #f9f9f9; }
blockquote {
    border-left: 4px solid #90caf9;
    margin: 12px 0;
    padding: 8px 16px;
    color: #555;
    background: #e3f2fd;
    border-radius: 0 4px 4px 0;
}
a { color: #1565c0; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 20px 0; }
"""

_MD_EXTENSIONS = ["tables", "fenced_code", "nl2br", "sane_lists"]


def md_to_pdf(md_path: Path, pdf_path: Path) -> None:
    text = md_path.read_text(encoding="utf-8")
    body = markdown.markdown(text, extensions=_MD_EXTENSIONS)
    html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><style>{_CSS}</style></head><body>{body}</body></html>"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html, base_url=str(md_path.parent)).write_pdf(str(pdf_path))
