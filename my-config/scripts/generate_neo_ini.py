#!/usr/bin/env python3
"""Build a candidate Neo INI from the synced base without changing the live template."""
from pathlib import Path
import argparse
import re
from datetime import datetime
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT / "cfg/Custom_Clash_Full_Fallback.ini"
ACTIVE = ROOT / "cfg/Neo_Clash_Full_Fallback.ini"
OUTPUT = ROOT / "my-config/build/Neo_Clash_Full_Fallback.candidate.ini"
PREFERRED = ["🇸🇬 新加坡节点", "🇯🇵 日本节点", "🇺🇸 美国节点", "🇰🇷 韩国节点", "🇭🇰 香港节点"]
EXCEPTIONS = {"📺 ABEMA", "🎮 DMM", "📺 Bahamut"}
TIMESTAMP_PREFIX = "; 最后更新（北京时间）："


def strip_timestamp(text):
    return "".join(line for line in text.splitlines(keepends=True) if not line.startswith(TIMESTAMP_PREFIX))

def transform(line):
    if not line.startswith("custom_proxy_group="):
        return line
    parts = line.split("`")
    if len(parts) < 3 or parts[1] not in {"fallback", "select"}:
        return line
    name = parts[0].removeprefix("custom_proxy_group=")
    if name in EXCEPTIONS:
        return line
    region_indices = [i for i, val in enumerate(parts) if val.startswith("[]") and val[2:].endswith("节点")]
    regions = [parts[i][2:] for i in region_indices]
    if not all(region in regions for region in PREFERRED):
        return line
    reordered = PREFERRED + [region for region in regions if region not in PREFERRED]
    assert len(reordered) == len(region_indices), "Duplicate or unexpected region group: " + name
    for i, region in zip(region_indices, reordered):
        parts[i] = "[]" + region
    return "`".join(parts)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Compare generated candidate against live Neo template")
    args = parser.parse_args()
    source = BASE.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)
    header = (
        "; NeoHeee 个人专属 OpenClash 订阅转换模板\n"
        "; 节点地区优先级（五个地区均存在时）：新加坡 > 日本 > 美国 > 韩国 > 香港\n"
        "; 特殊策略：保留直连优先分组及 ABEMA、DMM、Bahamut 等服务的原有地区优先级\n"
        "; 上游同步：基于 cfg/Custom_Clash_Full_Fallback.ini 生成，保持上游规则资源引用不变\n\n"
    )
    body = "".join(transform(line.rstrip("\r\n")) + line[len(line.rstrip("\r\n")):] for line in lines)
    # Timestamp only changes when template content changes, avoiding needless daily commits.
    unmarked = header + body
    previous = ACTIVE.read_text(encoding="utf-8") if ACTIVE.exists() else ""
    if previous and strip_timestamp(previous) == unmarked:
        match = re.search(r"^" + re.escape(TIMESTAMP_PREFIX) + r"(.+)$", previous, flags=re.MULTILINE)
        stamp = match.group(1) if match else datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
    else:
        stamp = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")
    result = header.replace("; NeoHeee 个人专属 OpenClash 订阅转换模板\n",
                            "; NeoHeee 个人专属 OpenClash 订阅转换模板\n" +
                            TIMESTAMP_PREFIX + stamp + "\n", 1) + body
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(result, encoding="utf-8")
    if args.check:
        live = ACTIVE.read_text(encoding="utf-8")
        if result != live:
            print("DRIFT: candidate differs from the deployed personal template; review the generated artifact before promotion.")
            raise SystemExit(2)
        print("PASS: candidate matches active Neo template.")
    else:
        print(f"Generated: {OUTPUT} (live template unchanged)")

if __name__ == "__main__":
    main()
