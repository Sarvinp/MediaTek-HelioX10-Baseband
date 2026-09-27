# fix/linux-build-nvram-cgen-link

Make the 2015 MOLY tree build on a modern Linux host. 2 commits — the foundation every other branch stands on.

## Problem
The tree shipped with a hard-coded 2015 toolchain setup that fails on current glibc/GCC: broken `compiler.mak` sections and `-fno-common` (unresolved duplicate symbols at link, notably NVRAM `cgen` tables).

## Commits
- `5b9630f` — Fix Linux MT6795 modem build through final link stage
- `72142b6` — Restore stock compiler.mak to fix toolchain sections and -fno-common

## Result
`make.sh` produces a complete `modem_1_lwg_n.img` (plus `.bin`/`.map`/`.sym` artifacts in `build/LCSH6795_LWT_L/LWG/bin/`). First MOLY image ever built from this tree.
