"""Export executed notebooks 04/05 as self-contained, code-hidden offline HTML."""

import html
from pathlib import Path

import nbformat
from nbconvert.filters.markdown import markdown2html

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "reports" / "visualization"
    output.mkdir(parents=True, exist_ok=True)
    for stem in ["04_visualization_comparison", "05_visualization_study_analysis"]:
        notebook = nbformat.read(ROOT / "notebooks" / f"{stem}.ipynb", as_version=4)
        parts = []
        for cell in notebook.cells:
            if cell.cell_type == "markdown":
                parts.append(str(markdown2html(cell.source)))
            for result in cell.get("outputs", []):
                if result.output_type == "error":
                    raise ValueError(f"Cannot publish notebook error: {result.ename}")
                data = result.get("data", {})
                if "image/png" in data:
                    parts.append(
                        f'<img alt="Atlas experiment figure" src="data:image/png;base64,{data["image/png"]}">'
                    )
                elif "text/html" in data:
                    parts.append(data["text/html"])
                elif "text/plain" in data:
                    parts.append(f"<pre>{html.escape(data['text/plain'])}</pre>")
                elif "text" in result:
                    parts.append(f"<pre>{html.escape(result.text)}</pre>")
        document = """<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Atlas · Mid-term research</title>
<style>body{max-width:1050px;margin:40px auto;padding:0 25px;background:#fffefa;color:#183332;
font:16px/1.65 system-ui,sans-serif}h1{font:42px/1.2 Georgia,serif;color:#166c60}h2{margin-top:45px}
table{border-collapse:collapse;width:100%;font-size:14px;display:block;overflow:auto}th,td{padding:10px;
border-bottom:1px solid #dce2d9;text-align:left}th{background:#edf2eb}pre{padding:15px;background:#f1f3ed;
overflow:auto;font-size:12px;white-space:pre-wrap}img{max-width:100%;height:auto}a{color:#166c60}
code{font-size:.9em}blockquote{border-left:3px solid #166c60;padding-left:20px}
@media print{body{margin:0;font-size:11px}h2{break-after:avoid}img{max-height:500px}}</style>
<body><p>ATLAS / OFFLINE MID-TERM DEMONSTRATION / 2 NOVEMBER 2026</p>"""
        document += "\n".join(parts) + "</body></html>"
        (output / f"{stem}.html").write_text(document)


if __name__ == "__main__":
    main()
