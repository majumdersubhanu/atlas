"""Make the current three-figure nbconvert presentation usable offline."""

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ALT_TEXT = [
    "Reported equity-to-assets ratios for the fixed 30-bank cohort in December 2019 and June 2020",
    "Observed S&P 500 prices and within-window drawdown, February to April 2020",
    "Modeled capital exhaustion and shortfall across assumed uniform asset impairments",
]
STYLE = (
    '<style id="atlas-offline">.atlas-equation{font-size:1.3em;padding:1em;background:#edf3f7}'
    "img{max-width:100%;height:auto}.jp-RenderedHTMLCommon{overflow-x:auto}</style>"
)


def finalize(html: str) -> str:
    """Remove scripts and describe the known figures; reject unexpected exports.

    This function is specific to notebook 03. Figure-count validation prevents
    assigning descriptions to unrelated figures after an authoring change.
    """
    if len(re.findall(r"<img\b[^>]*>", html, flags=re.IGNORECASE)) != len(ALT_TEXT):
        raise ValueError("Expected notebook 03's three figures; review descriptions before exporting")
    html = re.sub(r"<script\b[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(
        r"\$\$.*?\$\$",
        '<p class="atlas-equation">Lᵢ = qAᵢ &nbsp; · &nbsp; E′ᵢ = Eᵢ − Lᵢ &nbsp; · &nbsp; q*ᵢ = Eᵢ/Aᵢ</p>',
        html,
        flags=re.DOTALL,
    )
    descriptions = iter(ALT_TEXT)

    def describe(match: re.Match) -> str:
        tag = re.sub(r'\s+alt="[^"]*"', "", match.group(0), flags=re.IGNORECASE)
        return tag.removesuffix(">").removesuffix("/").rstrip() + f' alt="{next(descriptions)}">'

    html = re.sub(r"<img\b[^>]*>", describe, html, flags=re.IGNORECASE)
    html = re.sub(r'<style id="atlas-offline">.*?</style>', "", html, flags=re.DOTALL)
    return html.replace("</head>", STYLE + "</head>")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", type=Path, default=ROOT / "reports/03_real_data_defense.html")
    path = parser.parse_args().path
    result = finalize(path.read_text(encoding="utf-8"))
    path.write_text(result, encoding="utf-8")
    print("Static presentation: embedded figures, Unicode equations, no external scripts.")


if __name__ == "__main__":
    main()
