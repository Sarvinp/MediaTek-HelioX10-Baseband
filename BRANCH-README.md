# exp/ephy-mipi-check-nop

Get past the modem's own RF-table validation asserts — the bridge between "boots then instantly crashes" and "boots stable".

## What happened
With the HTC tail package, the MD booted ~2 s and died on `ephy_rf_error_check.c` asserts, looping with watchdog resets. The firmware was *validating its RF configuration tables* against expectations our generic MOLY data didn't meet (wrong sub-band table shapes, unknown write-sequence types).

## Commits
- `ed3dd32` — NOP the MIPI sub-band table asserts (first boot assert on HTC NVRAM gone)
- `b2cf74c` — extend NOP to all 20 ePHY RF validation sites
- `5a8825f` — **test(R3-C): modem BOOTS on device — baseband reports, stable, no WDT**
- `61e50cb` — analysis(R4): the SIM stall traces to a *swallowed* DSP assert `RFD_MIPIevent.c:134 @FMC`

## Key lesson
Assert-by-assert NOPing is a scalpel, not a fix: each bypass moved the crash to the next check (line 171 → 177 → 85 → MIPI 387 → 135 …) until boot stabilized. It proved the tables — not the code — were the real gap, which is exactly what `exp/htc-rf-transplant` then fixed properly by porting HTC's real tables. PC-side patch scripts for the image-level variants live in `tools-htc/modem-ver-9/` on the main line.
