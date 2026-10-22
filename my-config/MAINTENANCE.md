# NeoHeee OpenClash personal INI — maintenance and rollback

## Active and test configuration

- Production (unchanged): `main/cfg/Custom_Clash_Full_Fallback.ini`.
- Personal INI: `custom/cfg/Neo_Clash_Full_Fallback.ini`.
- NAS backend: `http://10.10.10.22:25500/sub` (LAN only).

This public repository must **never** contain node-provider tokens, subscription URLs containing secrets, or NAS credentials.

## Update model

1. `Sync Aethersailor Upstream` on `main` synchronizes non-workflow upstream changes into `upstream-sync`, then merges them into `custom`. It does not overwrite the personal INI by name.
2. The personal INI is a controlled **snapshot** of `custom/cfg/Custom_Clash_Full_Fallback.ini`, with ChatGPT candidates prioritized SG -> JP -> US -> HK.
3. The existing `Validate Personal OpenClash YAML` workflow (stored on `main`) invokes `python my-config/scripts/validate_ini.py` and the existing YAML checks against `custom`.
4. If upstream modifies the original INI, INI validation may fail intentionally: review upstream differences and manually rebase the personal snapshot before accepting them. **No automatic rewriting of the personal INI.**
5. GitHub validation does not test remote provider reachability, Mihomo core functionality or real DNS/IPv6 leakage. Test these on your router before switching production.

## Safe rollout

1. Check GitHub Actions: successful upstream sync and personal YAML+INI validation.
2. Submit personal INI in NAS `/inspect` using `config=https://raw.githubusercontent.com/NeoHeee/Custom_OpenClash_Rules/custom/cfg/Neo_Clash_Full_Fallback.ini`.
3. Save a backup of the working OpenClash configuration; test in a separate `Neo-Test` subscription.
4. Confirm HTTP 200, rulesets and groups, Mihomo syntax test, provider updates and actual traffic, including DNS and IPv6.
5. Only then change the active subscription's `config` parameter.

## Rollback

If the new template breaks, restore the known-good original template URL:

```text
https://raw.githubusercontent.com/NeoHeee/Custom_OpenClash_Rules/main/cfg/Custom_Clash_Full_Fallback.ini
```

Keep the same NAS `/sub` endpoint, `target`, subscription URL, and other query parameters. Update OpenClash and select the last working configuration if needed.

## Important limitations

- Region-level `url-test` measures latency only, not service unblocking.
- `fallback` checks health; a healthy exit may still fail ChatGPT's service requirements.
- Rules in the template still point to upstream-maintained remote assets.
- If upstream synchronization fails or INI drift validation fails, retain the existing working template and investigate; do not force-merge.
