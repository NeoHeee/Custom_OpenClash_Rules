# NeoHeee — 重度分流 Fallback 定制准备

## 已核对的上游文件

- 订阅转换模板: `cfg/Custom_Clash_Full_Fallback.ini`
- 最小 YAML: `cfg/yaml/Custom_Clash_Full_Fallback.yaml`
- 覆写模块: `overwrite/yaml/Custom_Clash_Full_Fallback.conf`（下载时 force=true；暂不使用）

本地生成脚本仅读取同步后的上游 YAML，不会更改其原文件。
DNS / IPv6 / TUN 由 OpenClash LuCI 管理，本阶段保持原样。

## 用法（在 custom 分支工作目录执行）

```sh
python -m pip install -r my-config/requirements.txt
python my-config/scripts/build.py --check
python my-config/scripts/build.py
```

生成文件在 `my-config/build/Custom_Clash_Full_Fallback_Neo.yaml`，已加入 .gitignore。
**构建输出仅用于离线检查**；不会自动推送、部署或更改路由器。

个人规则分别写入 `my-config/rules/direct.list`、
`proxy.list`、`reject.list`，一行一条，如 `DOMAIN-SUFFIX,example.com`。
支持 DOMAIN、DOMAIN-SUFFIX、DOMAIN-KEYWORD、IP-CIDR、IP-CIDR6。
保持规则排序：私有地址优先、个人规则次之、上游规则其后。

## 后续必要验证

1. 检查生成文件中 `proxy-providers.provider1.url` 仍为占位值，不要把订阅凭据提交公开仓库。
2. 以临时文件注入订阅并用 Mihomo `-t` 测试解析。
3. 核对各地区节点组不为空、Fallback 可跨地区、ChatGPT 实际可访问。
4. 检测 DNS、IPv4/IPv6 泄漏并确认 OpenClash LuCI 设置。
5. 验证通过再单独设计发布工作流和回滚方式。

本阶段未改动 `main` 同步工作流，也未启用额外 Actions。
