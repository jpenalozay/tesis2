"""Genera Parcial_Informe.pdf (informe académico UNI) desde parcial_informe.md."""

from pathlib import Path

import markdown
from weasyprint import HTML

HERE = Path(__file__).resolve().parent
MD = HERE / "parcial_informe.md"
PDF = HERE / "Parcial_Informe.pdf"

CSS = """
@page {
  size: A4;
  margin: 2.5cm 2.5cm 2.8cm 2.5cm;
  @bottom-center {
    content: counter(page);
    font-family: "Liberation Serif", "DejaVu Serif", "Times New Roman", serif;
    font-size: 10pt;
    color: #333;
  }
}
@page :first {
  margin: 2.5cm 2.5cm;
  @bottom-center { content: none; }
}
body {
  font-family: "Liberation Serif", "DejaVu Serif", "Times New Roman", serif;
  font-size: 12pt;
  line-height: 1.5;
  color: #000;
  text-align: justify;
  hyphens: auto;
}
.cover-page {
  page-break-after: always;
  min-height: 240mm;
  padding: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
  background: #fff;
}
.cover-page p,
.cover-page h1,
.cover-page h2,
.cover-page h3 {
  border: none;
  margin: 0;
  padding: 0;
  color: #000;
  font-weight: normal;
  text-align: center;
  width: 100%;
}
.cover-uni {
  font-size: 13pt;
  font-weight: bold;
  letter-spacing: 0.02em;
  margin-bottom: 4mm !important;
}
.cover-faculty {
  font-size: 11pt;
  margin-bottom: 18mm !important;
}
.cover-doc-type {
  font-size: 13pt;
  font-weight: bold;
  margin-bottom: 8mm !important;
}
.cover-title {
  font-size: 12pt;
  font-weight: bold;
  margin: 0 12mm 10mm 12mm !important;
  line-height: 1.45;
  text-align: center;
}
.cover-degree {
  font-size: 11pt;
  margin-bottom: 16mm !important;
  line-height: 1.45;
}
.cover-label {
  font-size: 11pt;
  font-weight: bold;
  margin-top: 6mm !important;
}
.cover-author {
  font-size: 12pt;
  margin-bottom: 4mm !important;
}
.cover-meta {
  font-size: 11pt;
  margin: 2mm 0 !important;
  line-height: 1.45;
}
.cover-place {
  font-size: 11pt;
  margin-top: 18mm !important;
  font-weight: bold;
}
.cover-page hr,
.cover-page table { display: none; }
h1 {
  font-size: 14pt;
  font-weight: bold;
  color: #000;
  border: none;
  margin-top: 0;
  margin-bottom: 6mm;
  text-align: left;
}
h2 {
  font-size: 12pt;
  font-weight: bold;
  color: #000;
  border: none;
  margin-top: 8mm;
  margin-bottom: 4mm;
  text-align: left;
}
h3 {
  font-size: 12pt;
  font-weight: bold;
  color: #000;
  margin-top: 6mm;
  margin-bottom: 3mm;
  text-align: left;
}
p {
  margin: 0 0 3mm 0;
  text-align: justify;
}
ul, ol {
  margin: 2mm 0 4mm 0;
  padding-left: 8mm;
}
li { margin-bottom: 1.5mm; }
table {
  border-collapse: collapse;
  width: 100%;
  margin: 4mm 0 6mm 0;
  font-size: 10.5pt;
  line-height: 1.35;
}
th, td {
  border: 1px solid #000;
  padding: 2.5mm 3mm;
  vertical-align: top;
  text-align: left;
}
th {
  font-weight: bold;
  background: #fff;
  color: #000;
}
tr:nth-child(even) td { background: #fff; }
blockquote {
  margin: 4mm 0 4mm 8mm;
  padding: 0;
  border: none;
  font-style: italic;
  color: #000;
  text-align: justify;
}
hr {
  border: none;
  border-top: 1px solid #000;
  margin: 6mm 0;
}
strong { font-weight: bold; }
em { font-style: italic; color: #000; }
code {
  font-family: "Liberation Mono", "DejaVu Sans Mono", monospace;
  font-size: 10pt;
  color: #000;
}
a { color: #000; text-decoration: none; }
"""


def main() -> None:
    raw = MD.read_text(encoding="utf-8")
    html_body = markdown.markdown(
        raw,
        extensions=["tables", "fenced_code", "sane_lists", "attr_list"],
    )
    html = (
        f"<html><head><meta charset='utf-8'>"
        f"<style>{CSS}</style></head>"
        f"<body>{html_body}</body></html>"
    )
    HTML(string=html, base_url=str(HERE) + "/").write_pdf(str(PDF))
    print(f"PDF generado: {PDF}")


if __name__ == "__main__":
    main()
