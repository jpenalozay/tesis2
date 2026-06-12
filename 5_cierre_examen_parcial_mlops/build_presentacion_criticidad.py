"""Convierte presentacion_modulo_criticidad.md a PDF apaisado."""

import re
from pathlib import Path

import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
MD = HERE / "presentacion_modulo_criticidad.md"
PDF = HERE / "Presentacion_Modulo_Criticidad.pdf"

CSS = """
@page { size: 297mm 167mm; margin: 0; }
.slide { page-break-after: always; width: 297mm; height: 167mm; padding: 12mm 16mm; box-sizing: border-box; overflow: hidden; }
.slide h1 { font-size: 26px; color: #0d2a4d; border-bottom: 3px solid #b3132c; }
.slide h2 { font-size: 19px; color: #20456e; }
.slide p, .slide li { font-size: 14.5px; line-height: 1.5; }
.slide table { border-collapse: collapse; width: 100%; font-size: 12.5px; }
.slide th { background: #0d2a4d; color: #fff; padding: 5px 8px; }
.slide td { border: 1px solid #c9d3df; padding: 4.5px 8px; }
.slide pre { font-size: 10.5px; background: #f4f6f8; padding: 8px; border-radius: 4px; white-space: pre-wrap; }
.slide img { max-width: 92%; max-height: 95mm; display: block; margin: 6px auto; }
.slide.title-slide { background: #0d2a4d; color: #fff; display: flex; flex-direction: column; justify-content: center; }
.slide.title-slide h1 { color: #fff; font-size: 32px; border-bottom-color: #b3132c; }
.slide.title-slide h2, .slide.title-slide p { color: #e8eef5; }
"""

raw = MD.read_text(encoding="utf-8")
raw = re.sub(r"\A---\nmarp:.*?\n---\n", "", raw, flags=re.DOTALL)
chunks = [c.strip() for c in re.split(r"\n---\n", raw) if c.strip()]
slides = []
for i, chunk in enumerate(chunks):
    body = markdown.markdown(chunk, extensions=["tables", "sane_lists", "fenced_code"])
    klass = "slide title-slide" if i == 0 else "slide"
    slides.append(f'<div class="{klass}">{body}</div>')
html = f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{''.join(slides)}</body></html>"
HTML(string=html, base_url=str(HERE) + "/").write_pdf(str(PDF))
print(f"Slides: {len(chunks)} | PDF: {PDF}")
