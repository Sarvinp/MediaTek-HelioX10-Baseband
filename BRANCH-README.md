# exp/md-boot-htc-tail

**The boot breakthrough.** This is where the self-built MOLY modem first came alive on the HTC device.

## The finding
Comparing the stock HTC modem image byte-by-byte with ours revealed a 148-byte trailer ours lacked: after the payload, stock carries a signature region ending in `EEEE…EEEE` + `FFFFFFFF`. The AP-side loader (`ccci_mdinit`) reads this tail as part of image validation.

Without it: image "loads", `md_power_on()` runs — and the modem **never executes a single instruction** (CLDMA clock stays off, forever). With it: same driver path, but `CLDMA clock is on` appears and the MD starts running.

## Commits
- `4f023a6` — graft the stock 148-byte MD tail (EEEE region table) onto the MOLY image
- `481060e` — analysis: round-1 legacy-header test was invalid; pristine tail is byte-identical to stock
- `76dba66` — first real device test of the pristine package: image loads, **modem boots and immediately asserts** (`ephy_rf_error_check.c`) — which proved execution and handed the problem to `exp/ephy-mipi-check-nop`

## Why it matters
Every later branch builds on this packaging. The required device-side state: patched boot kernel (`boot-htcfix5`) so `SEC_CCCI` signature verification passes despite the non-HTC signature.
