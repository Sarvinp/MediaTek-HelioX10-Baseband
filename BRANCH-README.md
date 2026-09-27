# stable/htc-moly-cgmr-atcmd

First *stable, device-usable* MOLY build. 3 commits (2 build fixes + this). Tag: `htc-moly-stable-v1`.

## What it fixes
1. **`AT+CGMR` crash** — stock HTC RIL queries the modem version on boot; MOLY's `libl4.a` answered `+CGMR: %s, %s` (two-arg format into a one-arg path), crashing the AT parser. Patched the format string in `libl4.a` to `+CGMR: %s`.
2. **Missing HTC vendor AT commands** — the HTC RIL polls commands MOLY never heard of, stalling init. Added `AT+HTCSBP`, `AT+HTCTEST`, `AT+EIMS`, `AT+ERLM`, `AT+CGREG`, `AT+CAPL` to `custom/modem/common/ps/customer_at_command.c`.

## Where things stood at this tag
Image builds, installs, AP talks to it — but the modem would not yet boot on the HTC hardware (solved later in `exp/md-boot-htc-tail`). This branch is the preserved "known-good build fixes" baseline that all later experiment branches fork from.
