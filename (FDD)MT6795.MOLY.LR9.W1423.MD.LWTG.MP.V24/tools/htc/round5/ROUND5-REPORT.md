# Round 5 — HTC RF Data Transplant (2026-09-19 night, modem-ver-11)

## What was done
Ported HTC stock's real RF MIPI data into the MOLY V24 image, on top of the
R3-C no-asserts base:

1. **GGE (2G) MIPI tables** — full transplant (RX/TX events+rows+PA data,
   4 bands: GSM850/900/1800/1900). Layouts byte-verified on both sides
   (events 13x10B @+0, RX rows 30x48B @+130, TX events @+1578, TX rows
   @+1708, PA @+3148). TRUE cluster located via ELF-symbol spacing
   0x1a60/0x3480/0x1a68 → img 0x848e0c/0x84a86c/0x84dcec/0x84f754
   (first attempt hit identical generic copies at wrong offsets — caught).
2. **LTE MIPI DATA tables** — 13 tables (B1/B3/B5/B7/B8/B38/B39/B40 RX+TX)
   via arfcn anchors (LTE row = 48B, arfcn u16 @+8). B17/B41 absent in stock
   (device doesn't support them). 877B changed.
3. **UMTS MIPI DATA tables** — 8 tables (B1/B2/B5/B8 RX+TX, 68B rows,
   arfcn u32 @+8, tables 1836-2040B). B3/B4 anchors missed (subband
   granularity differs in stock) — left generic. 719B changed.

## Test results (all with live asserts where relevant)
- diag+GGE:           still `RFD_MIPIevent.c:134 @FMC` → SIM NOT_READY
- diag+GGE+LTE:       still same assert
- diag+GGE+LTE+UMTS:  still same assert
→ The DSP-side check is NOT fed by the DATA tables alone.
  Next lever: LTE/UMTS **EVENT** tables (the assert names RFD_MIPI**event**),
  plus TPC/BYPASS families.

## End state (stable, on-phone now)
`modem_1_lwg_n.img.htc-rf-prod.img` (sha256 939ac2c1…) = no-asserts base +
all HTC data transplants. Boots, stable, 0 exceptions, USIM detected,
SIM NOT_READY (assert-swallow stall persists via DSP check).

## Images (this dir)
- modem_1_lwg_n.img.gge-htc.img          (no-asserts + GGE)
- modem_1_lwg_n.img.diag-gge.img         (diag asserts + GGE)
- modem_1_lwg_n.img.diag-gge-lte.img     (+ LTE data)
- modem_1_lwg_n.img.diag-gge-lte-umts.img(+ UMTS data)
- modem_1_lwg_n.img.htc-rf-prod.img      (production: no-asserts + all data)
- gge_ours.bin, mipi_ev_symbols.txt, ul1_probe.bin (analysis artifacts)
- tools/transplant_gge_true.py, transplant_lte.py (reproducible pipelines)

Rollback unchanged: /data/local/tmp/stock_modem.img + stock_dsp.bin.
