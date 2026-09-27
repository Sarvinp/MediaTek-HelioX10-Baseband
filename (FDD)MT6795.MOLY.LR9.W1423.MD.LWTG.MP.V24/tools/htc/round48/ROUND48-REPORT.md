# Round 48 — GGE Events Source-Ported & Built: DSP RF Assert CLEARED (modem-ver-48)

## Extraction (completed)
- 12B-row shape-scan over stock image: 75 LTE event tables; ALL 13
  R12 anchor events confirmed (B1/B3/B5/B7/B8/B38/B39/B40 TX+RX)
- GGE 10B-row scan (sGGE_MIPIEVENT = u16 elm,st,sp,type + s16 tm):
  8 tables @0x89d8cc-0x8a06a0 = 4 bands x RX(n=4)/TX(n=7)
- Hardware-consistent pairing: 850/1900 share TX timings, 900/1800 share

## Source port (commit a5a87fc)
- l1d_custom_mipi.c: all 8 GGE event blocks replaced with HTC values
  (7 real TX events incl PA+ASM+ANT vs 3 generic before)
- Native rebuild OK; HTC timings verified in new ELF .data

## r48 image (sha 18c070ffcf5dc95e)
= rebuild(GGE events + t0_guard) + 18 ephy nops + 2 mml1 + 6 wrevent
  + fix2 FE01 gate force (all re-resolved by symbol)

## RESULT — MAJOR MOVEMENT
- **RFD_MIPIevent.c:134 @FMC assert is GONE** (was the bars blocker
  since R4!) — the GGE event port satisfied the DSP validation
- New (later-stage) assert: nvram_io.c:1211, LID=164, at ~5min
  = LTE MIPI NVRAM read+recover failing (EL1 family)
  = the LTE EVENT tables are still MOLY-generic in the NVRAM regen
  path (we ported LTE DATA only, R12)
- SIM: NOT_READY unchanged (fix2 line intact)

## Next (ver-49)
Port the 25 stock LTE event tables into lte_custom_mipi.c (corpus
already in stock_events.json with R12 anchor mapping), rebuild,
reflash → target: nvram_io assert gone → RF config completes →
network search survives → BARS.

## Status
Phone on r48 (stable boots; late nvram assert loop stage-2).
