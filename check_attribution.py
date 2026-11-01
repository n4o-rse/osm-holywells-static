"""Checks that the attribution travels with the published data (PRIMER.md, S8): the ODbL asks for "© OpenStreetMap contributors".

    python check_attribution.py

Looks at the pages in docs/ (the redirect pages in docs/entity/ are exempt), the Turtle files of the entities in docs/ttl/ and the
export in dist/, and at the licence in site.yaml. Writes nothing; exit code 1 and a list of the files that lack the text otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TEXT = "OpenStreetMap contributors"


def main() -> int:
    files = [p for pattern, folder in (("*.html", "docs"), ("*.ttl", "docs/ttl"), ("*.ttl", "dist")) for p in sorted((ROOT / folder).glob(pattern))]
    files.append(ROOT / "site.yaml")
    missing = [p for p in files if TEXT not in p.read_text(encoding="utf-8")]
    if not files[:-1]:
        print("ERROR: [attribution] no page or Turtle file found; run python main.py first")
        return 1
    if missing:
        print(f"ERROR: [attribution] {len(missing)} file(s) lack \"{TEXT}\":")
        for path in missing[:20]:
            print(f"  {path.relative_to(ROOT).as_posix()}")
        return 1
    print(f"[attribution] \"{TEXT}\" is in {len(files)} file(s): pages, entity Turtle files, the export, site.yaml")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
