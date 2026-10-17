#!/usr/bin/env python3
"""Build an isolated OpenClash test YAML without changing upstream files."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
import yaml

ROOT = Path(__file__).resolve().parents[2]
ALLOWED_TYPES = {"DOMAIN", "DOMAIN-SUFFIX", "DOMAIN-KEYWORD", "IP-CIDR", "IP-CIDR6"}

def read_rules(path: Path, target: str):
    output = []
    if not path.is_file():
        raise ValueError(f"Missing rule file: {path}")
    for index, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [v.strip() for v in line.split(",")]
        if len(parts) != 2 or parts[0] not in ALLOWED_TYPES or not parts[1]:
            raise ValueError(f"Invalid rule {path}:{index}: {line}")
        if any(c.isspace() for c in parts[1]):
            raise ValueError(f"Whitespace in rule {path}:{index}")
        rule = f"{parts[0]},{parts[1]},{target}"
        if parts[0] in ("IP-CIDR", "IP-CIDR6"):
            rule += ",no-resolve"
        output.append(rule)
    return output

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--profile", default="my-config/profile.yaml")
    ap.add_argument("--check", action="store_true", help="Validate without writing output")
    args = ap.parse_args()
    profile = yaml.safe_load((ROOT / args.profile).read_text(encoding="utf-8"))
    source = ROOT / profile["base"]
    destination = ROOT / profile["output"]
    if not source.is_file():
        raise ValueError(f"Upstream YAML missing: {source}")
    config = yaml.safe_load(source.read_text(encoding="utf-8"))
    if not isinstance(config, dict) or not isinstance(config.get("rules"), list):
        raise ValueError("Upstream config must contain a rules list")
    names = {x["name"] for x in config.get("proxy-groups", [])}
    extras = []
    for item in profile["rule_files"]:
        target = item["target"]
        if target not in names and target not in {"DIRECT", "REJECT"}:
            raise ValueError(f"Unknown policy group: {target}")
        extras.extend(read_rules(ROOT / item["path"], target))
    # Keep GEOSITE/private and GEOIP/private above personal rules.
    rules = config["rules"]
    if rules[:2] != ["GEOSITE,private,🎯 全球直连",
                      "GEOIP,private,🎯 全球直连,no-resolve"]:
        raise ValueError("Upstream private-network rule order changed: review required")
    config["rules"] = rules[:2] + list(dict.fromkeys(extras)) + rules[2:]
    if config.get("dns") is not None or config.get("ipv6") is not None:
        print("Note: upstream now contains DNS/IPv6; values preserved unchanged")
    rendered = yaml.safe_dump(config, allow_unicode=True, sort_keys=False)
    checked = yaml.safe_load(rendered)
    assert checked["rules"] == config["rules"]
    print(f"Validated: {len(names)} groups; {len(rules)} upstream rules; {len(extras)} personal rules")
    if not args.check:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text("# Generated test configuration; do not add subscription credentials here.\n" + rendered, encoding="utf-8")
        print(f"Wrote {destination.relative_to(ROOT)}")

if __name__ == "__main__":
    try:
        main()
    except (OSError, KeyError, TypeError, ValueError, yaml.YAMLError) as exc:
        print(f"Build rejected: {exc}", file=sys.stderr)
        sys.exit(1)
