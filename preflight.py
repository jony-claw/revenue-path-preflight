#!/usr/bin/env python3
"""Deterministic preflight for creator revenue paths.

No credentials are read. The tool evaluates declared capabilities against a dated,
source-backed rule set. It does not promise account approval or revenue.
"""
from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any

DATA_PATH = Path(__file__).with_name("platforms.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(profile: dict[str, Any], catalog: dict[str, Any]) -> dict[str, Any]:
    country = str(profile.get("country", "")).upper()
    capabilities = set(profile.get("capabilities", []))
    results = []
    for platform in catalog["platforms"]:
        if country not in platform.get("countries", [country]):
            results.append({
                "platform": platform["name"],
                "status": "blocked",
                "blockers": [f"country_not_confirmed:{country}"],
                "warnings": platform.get("warnings", []),
                "sources": platform["sources"],
            })
            continue
        missing_listing = [x for x in platform.get("listing_requires", []) if x not in capabilities]
        missing_payout = [x for x in platform.get("payout_requires", []) if x not in capabilities]
        if missing_listing:
            status = "blocked"
            blockers = [f"missing:{x}" for x in missing_listing]
        elif platform.get("revenue_capable", True) is False:
            status = "distribution_only"
            blockers = ["no_builtin_payment"]
        elif missing_payout:
            status = "listing_only"
            blockers = [f"payout_missing:{x}" for x in missing_payout]
        else:
            status = "payment_path_ready"
            blockers = []
        results.append({
            "platform": platform["name"],
            "status": status,
            "blockers": blockers,
            "fees": platform.get("fees"),
            "discovery": platform.get("discovery"),
            "warnings": platform.get("warnings", []),
            "sources": platform["sources"],
        })
    rank = {"payment_path_ready": 0, "listing_only": 1, "distribution_only": 2, "blocked": 3}
    results.sort(key=lambda x: (rank[x["status"]], x["platform"]))
    return {
        "generated_on": date.today().isoformat(),
        "catalog_checked_on": catalog["checked_on"],
        "country": country,
        "declared_capabilities": sorted(capabilities),
        "results": results,
        "summary": {
            key: sum(r["status"] == key for r in results)
            for key in ("payment_path_ready", "listing_only", "distribution_only", "blocked")
        },
        "disclaimer": "Preflight only: platform approval, KYC and real demand are not guaranteed.",
    }


def markdown(report: dict[str, Any]) -> str:
    lines = [
        "# Revenue path preflight",
        "",
        f"Country: `{report['country']}`  ",
        f"Catalog checked: `{report['catalog_checked_on']}`  ",
        f"Run date: `{report['generated_on']}`",
        "",
        "| Platform | Status | Blockers | Fees / caveats |",
        "|---|---|---|---|",
    ]
    for row in report["results"]:
        blockers = ", ".join(row["blockers"]) or "none declared"
        caveat = "; ".join(filter(None, [row.get("fees", ""), *row.get("warnings", [])]))
        lines.append(f"| {row['platform']} | {row['status']} | {blockers} | {caveat} |")
    lines += ["", report["disclaimer"], "", "## Sources"]
    seen = set()
    for row in report["results"]:
        for source in row["sources"]:
            if source not in seen:
                seen.add(source)
                lines.append(f"- {source}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check payout and listing prerequisites before building")
    parser.add_argument("profile", type=Path, help="JSON profile with country and capabilities")
    parser.add_argument("--catalog", type=Path, default=DATA_PATH)
    parser.add_argument("--format", choices=("json", "markdown"), default="markdown")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fail-if-no-payment-path", action="store_true")
    args = parser.parse_args()
    report = evaluate(load_json(args.profile), load_json(args.catalog))
    text = json.dumps(report, indent=2, ensure_ascii=False) + "\n" if args.format == "json" else markdown(report)
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    if args.fail_if_no_payment_path and report["summary"]["payment_path_ready"] == 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
