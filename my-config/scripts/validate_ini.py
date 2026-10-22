#!/usr/bin/env python3
"""Validate personal INI syntax, rules and permitted regional reordering."""
from pathlib import Path
from collections import Counter

root = Path(__file__).resolve().parents[2]
base = (root / "cfg/Custom_Clash_Full_Fallback.ini").read_text(encoding="utf-8")
personal = (root / "cfg/Neo_Clash_Full_Fallback.ini").read_text(encoding="utf-8")
preferred = ["🇯🇵 日本节点", "🇸🇬 新加坡节点", "🇺🇸 美国节点", "🇰🇷 韩国节点", "🇭🇰 香港节点"]
exceptions = {"📺 ABEMA", "🎮 DMM", "📺 Bahamut"}

def extract(text):
    lines = text.splitlines()
    assert lines.count("[custom]") == 1, "Expected exactly one [custom] section"
    rules = [s for s in lines if s.startswith("ruleset=")]
    groups = [s for s in lines if s.startswith("custom_proxy_group=")]
    result = {}
    for s in groups:
        assert "节点[]`" not in s and "``[]" not in s, "Malformed group delimiter: " + s[:55]
        parts = s.split("`")
        assert len(parts) >= 3, "Invalid group definition"
        name = parts[0].removeprefix("custom_proxy_group=")
        assert name not in result, "Duplicate policy group: " + name
        assert parts[1] in {"fallback", "select", "url-test", "load-balance"}, "Unexpected group type: " + name
        for x in parts[2:]:
            if x.startswith("[]"):
                assert len(x) > 2, "Empty group reference"
            elif x.endswith("节点") and not x.startswith("("):
                raise AssertionError("Malformed group reference in " + name + ": " + x)
        result[name] = parts
    return rules, result

baseline_rules, baseline_groups = extract(base)
personal_rules, personal_groups = extract(personal)
assert personal_rules == baseline_rules, "Ruleset order or content drifted"
assert personal_groups.keys() == baseline_groups.keys(), "Policy group names changed"
count = 0
for name, original in baseline_groups.items():
    actual = personal_groups[name]
    assert original[:2] == actual[:2], "Changed group type/name: " + name
    if name in exceptions or original[1] not in {"select", "fallback"}:
        assert original == actual, "Unexpected change in exception or region-test group: " + name
        continue
    a = original[2:]
    b = actual[2:]
    assert Counter(a) == Counter(b), "Changed candidates, URL, or interval: " + name
    if not all("[]" + r in a for r in preferred):
        assert a == b, "Changed group lacking all preferred regions: " + name
        continue
    # Only regional node-group positions can be moved.
    indices = [i for i, x in enumerate(a) if x.startswith("[]") and x[2:].endswith("节点")]
    assert [a[i] for i in range(len(a)) if i not in indices] == [b[i] for i in range(len(b)) if i not in indices], "Non-region entries changed: " + name
    candidates = [b[i][2:] for i in indices]
    assert candidates[:5] == preferred, "Incorrect regional priority: " + name
    assert candidates[5:] == [a[i][2:] for i in indices if a[i][2:] not in preferred], "Other regions changed order: " + name
    count += 1
print(f"PASS: {len(personal_rules)} rulesets; {len(personal_groups)} groups; {count} priority groups; valid separators.")
