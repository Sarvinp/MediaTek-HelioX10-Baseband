#!/bin/bash
# R39d STABLE REBUILD PROCEDURE (produces image identical to r39d)
# 1) build:   perl make.pl "LCSH6795_LWT_L(LWG).mak" u
# 2) nop:     python3 tools/htc/round39/apply_ephy_nops.py  (by symbol, EVEN addr)
# 3) pack:    stock 64B header + payload (pack_htc_modem.py)
set -e
cd "$(dirname "$0")/../../../.."
perl make.pl "LCSH6795_LWT_L(LWG).mak" u
python3 tools/htc/round39/apply_ephy_nops.py
echo "payload at build/.../LCSH6795_LWT_L_MDBIN_PCB01_MT6795_S00.MOLY_LR9_W1423_MD_LWTG_MP_V24.bin (nopped in place by script)"
