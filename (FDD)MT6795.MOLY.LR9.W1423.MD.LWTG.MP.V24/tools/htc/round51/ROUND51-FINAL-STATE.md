# Round 51 FINAL STATE — UMTS Port Aborts Bisected; Assert Hunt Advanced (modem-ver-51)

## Commits this round
- 36af133 revert nvram assert->trace patches (caused fat_backup continuation abort)
- f31dcc5 UMTS BandNone null-only (didn't fix abort)
- 7470e73 full UMTS port (corrected events ASM{0,1}+ANT{2,5} + DATA B1/B2/B4/B8
  with port-field mapping 2->PORT1) — STILL aborts
- 111b483 UMTS port OUT (all 4 variants data-abort; MOLY-generic = stable)
- 3e6c222 LTE BandNone event tables populated (r51g) — assert STILL fires

## Bisect table
| build | UMTS | result |
|-------|------|--------|
| r50   | MOLY generic | CLEAN; home registration ~12min; RFD assert 0,0,0 kills it |
| r50b/r51/r51b/r51c/r51e | any HTC content | data abort 3-10min in nvram_drv_fat_backup |
| r51g  | MOLY + LTE BandNone fill | assert at ~7min (unchanged) |

## Key discoveries
1. RFD_MIPIevent.c is DSP-side (not in ARM tree/DbgInfo) — cannot source-patch
2. /sys/kernel/ccci/debug=1 HALTS the DSP dump thread: 23min clean, registered,
   but NO RSSI (SignalStrength 99) and no asserts — DSP effectively dead-locked
   in the same walk. debug=0 -> assert returns in ~5min.
   => the assert and the missing RSSI are ONE bug: the DSP MIPI event walk never
   completes in our images, ever (SignalStrength was 99 in every build, even
   23-min registered boots)
3. MD exception call chain (from CCCI dump): irq_gcc -> ex_hdlr_gcc -> assert;
   assert args all zero = NULL-table sanity check in DSP FMC (flight-mode-control)
   RF on/off sequence
4. Full MD EX dump unavailable ("Dump MD EX log disabled"); mdlogger -s MD_EX
   running but captured nothing to /data/mdlog (config needed)
5. Stale EL4* NVRAM files = BP offsets (not events); deletion/restoration made
   no difference to the abort
6. Stock UMTS DATA tables found (68B rows, u32 subband fields): B1@0x892a88,
   B2@0x892f50, B5@0x893418, B8@0x893a00, TX sets @0x891f64/0x893fb4/0x894eac

## Phone state (r51g on board)
Stable Android; MD registers 'home' voice-regist-2 for ~5-12min windows; no RSSI;
RFD assert loop eventually resets MD. ccci debug back to 0.

## Remaining paths to bars
A. mdlogger proper config (mobilelog/md_ex capture) -> full DSP PC/registers at
   assert -> identify the exact NULL table the DSP wants
B. Reverse the MMMD DSP blob's RFD_MIPIevent walk (find expected table shape)
C. Diff stock's ARM->DSP shared-memory init vs ours (the DSP is fed via smem
   structures at MD boot — maybe the init code copies from tables that are
   still MOLY-generic: candidate = LTE/GGE DATA 'expand' tables and the
   BAND master arrays)
