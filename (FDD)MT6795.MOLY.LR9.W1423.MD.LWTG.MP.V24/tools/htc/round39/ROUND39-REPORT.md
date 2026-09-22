# Round 39 — Source Fix Built; R39 Regression Found & Fixed; r39c Ready (modem-ver-39)

## Why SIM is NOT READY (complete answer)
External SIM reads (PHB records, L4C IMSI/security) hang forever in
the uncapped T=0 status-word loop of L1sim_Cmd_Layer_MTK → AL never
returns → no CNF ever → SIM stuck DETECTED → NOT_READY. (R33-R38 proof chain.)

## The source fix (commit 0263859)
t0_guard cap (64) in driver/devdrv/usim/src/icc_switchControl_mtk_0.c:4499.
FIRST native rebuild succeeded (perl make.pl "LCSH6795_LWT_L(LWG).mak" u;
tools/tools/pack_dep_gen.pm shim needed). Guard verified in ELF+img.

## R39 flash → REGRESSION (my error, own it)
I assumed "rebuild = r12c + 7 lines". WRONG: r12c-prod carried
POST-LINK image patches — the R3-B 20-site ephy nop family. Fresh
link had live RF dev-checks → ephy_rf_error_check.c:171 assert →
MD reset loop (phone auto-recovered to fix6clean; no user impact).
Diff told the truth: 6.88M bytes ≠ "7 lines".

## Recovery → r39c (commit 310f7cc)
- Restored nop-patched libephy.a (2 sites) — insufficient
- TRUE fix: re-applied ALL 18 checker sites BY SYMBOL NAME from the
  new ELF (old absolute offsets invalid after rebuild — caught
  before flashing a corrupt image)
- r39c image verified on PC: guard @0x10D67C + nops (bx lr) at
  0x1ECE99 / 0x1ECB39 / all 18 sites
- modem_1_lwg_n.img.r39c-t0guard-ephy18.img, 8997296 B,
  sha 41012ea9f858eacb

## State
Phone: fix6clean (stable, 0 exc). r39c ready on PC.
Awaiting explicit GO to flash r39c.

## Expected on flash
Same stable RF behavior as r12c-era (checks nopped) + hung reads now
return FAIL after 64 iters → error CNF flows → SIM state machine
advances for the first time since R18.
