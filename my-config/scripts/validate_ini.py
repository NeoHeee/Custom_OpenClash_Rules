#!/usr/bin/env python3
"""Validate Neo's standalone INI against the upstream-derived custom-branch baseline.

Run: python my-config/scripts/validate_ini.py
"""
from pathlib import Path

root = Path(__file__).resolve().parents[2]
base = (root / "cfg/Custom_Clash_Full_Fallback.ini").read_text(encoding="utf-8")
neo = (root / "cfg/Neo_Clash_Full_Fallback.ini").read_text(encoding="utf-8")
base_lines = base.splitlines()
neo_lines = [line for line in neo.splitlines() if not line.startswith("; NeoHeee personal ") and not line.startswith("; Based on ") and not line.startswith("; Personal delta: ") and not line.startswith("; Upstream rule references remain ")]

def significant(lines):
    return [line for line in lines if line.startswith(("ruleset=", "custom_proxy_group="))]

a, b = significant(base_lines), significant(neo_lines)
assert len([x for x in b if x.startswith("ruleset=")]) == len([x for x in a if x.startswith("ruleset=")]), "Ruleset count changed"
assert [x for x in b if x.startswith("ruleset=")] == [x for x in a if x.startswith("ruleset=")], "Ruleset ordering/content drift"
base_groups = {x.split("`",1)[0]:x for x in a if x.startswith("custom_proxy_group=")}
neo_groups = {x.split("`",1)[0]:x for x in b if x.startswith("custom_proxy_group=")}
assert base_groups.keys() == neo_groups.keys(), "Policy groups changed"
chat = "custom_proxy_group=🤖 ChatGPT"
for key in base_groups:
    if key != chat:
        assert base_groups[key] == neo_groups[key], f"Unexpected personal group drift: {key}"
assert chat in neo_groups and "`fallback`[]🇸🇬 新加坡节点`[]🇯🇵 日本节点`[]🇺🇸 美国节点`[]🇭🇰 香港节点" in neo_groups[chat], "ChatGPT fallback order unexpected"
assert "`url-test`" in neo_groups["custom_proxy_group=🇸🇬 新加坡节点"]
print("PASS: INI rules, all policy groups, regional url-test and ChatGPT fallback checked.")
