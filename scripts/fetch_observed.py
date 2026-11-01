"""Explicit online refresh into a NEW directory; never overwrite the frozen demo."""

import argparse
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--output", type=Path, required=True)
    a = p.parse_args()
    a.output.mkdir(parents=True, exist_ok=False)
    manifest = []
    for date in ["20191231", "20200630"]:
        query = urlencode(
            {
                "filters": f"REPDTE:{date}",
                "fields": "CERT,CERTCONS,BKCLASS,NAME,REPDTE,ASSET,EQ,EQTOT,DEP,LIAB",
                "sort_by": "ASSET",
                "sort_order": "DESC",
                "limit": 100,
                "format": "json",
            }
        )
        url = "https://api.fdic.gov/banks/financials?" + query
        with urlopen(url, timeout=60) as r:
            body = r.read()
        payload = json.loads(body)
        if len(payload.get("data", [])) != 100:
            raise ValueError("Unexpected source row count")
        path = a.output / f"fdic_{date}.json"
        path.write_bytes(body)
        manifest.append(
            {
                "file": path.name,
                "source": url,
                "sha256": hashlib.sha256(body).hexdigest(),
                "retrieved": datetime.now(UTC).isoformat(),
            }
        )
    (a.output / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("Fresh snapshots saved. Audit before replacing the frozen presentation inputs.")


if __name__ == "__main__":
    main()
