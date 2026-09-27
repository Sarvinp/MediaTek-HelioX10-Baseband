#!/usr/bin/env python3
"""R48: build r48 image = fresh rebuild (GGE events + t0_guard) + nop family + fix2 gate.

Applied to the fresh .bin:
1. 18 ephy checker nops (symbol-resolved, EVEN addrs)
2. 2 mml1_rf_mipi assert nops (0x477678, 0x477688)
3. 6 wrevent_mipi assert nops (0x305d6..0x30e08)
4. fix2: movw r2,#0xfe01 at 0x4f19cc (FE01 gate force)
All addresses re-resolved by symbol from the NEW ELF where applicable.
"""
import subprocess, struct, hashlib

ROOT = "/root/MediaTek-HelioX10-Baseband/(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24"
ELF = ROOT + "/build/LCSH6795_LWT_L/LWG/bin/LCSH6795_LWT_L_MDBIN_PCB01_MT6795_S00.elf"
BIN = ROOT + "/build/LCSH6795_LWT_L/LWG/bin/LCSH6795_LWT_L_MDBIN_PCB01_MT6795_S00.MOLY_LR9_W1423_MD_LWTG_MP_V24.bin"

syms = subprocess.run(["readelf", "-sW", ELF], capture_output=True, text=True).stdout
funcs = {}
for l in syms.splitlines():
    p = l.split()
    if len(p) >= 8 and p[3] == "FUNC":
        try:
            funcs.setdefault(p[7], int(p[1], 16) & ~1)
        except Exception:
            pass

d = bytearray(open(BIN, "rb").read())

names = ["EPHY_ErrorCheck_Data_Seq_Type", "EPHY_ErrorCheck_SubFreq_Lower_Bound", "EPHY_ErrorCheck_SubFreq_Upper_Bound",
"EPHY_ErrorCheck_SubFreq_Zero", "EPHY_ErrorCheck_SubFreq_Max", "EPHY_ErrorCheck_TPC_Data_Num", "EPHY_ErrorCheck_IMM_Data_Num",
"EPHY_ErrorCheck_TPC_ELM_Type", "EPHY_ErrorCheck_TRx_Event_Type", "EPHY_ErrorCheck_TRx_Event_Data_Num",
"EPHY_ErrorCheck_TPC_Event_Data_Num", "EPHY_ErrorCheck_MAX_Event_Data_Num", "EPHY_RF_CheckSplitIndTable",
"EPHY_RF_CheckRFMipiDataTable", "EPHY_RF_CheckRFMipiBypassDataTable", "ephy_check_subband_MipiDataTable",
"ephy_check_subband_MipiTpcSectionData.part.5", "EPHY_ErrorCheck_Subband_MipiTpcSectionData"]
n = 0
for nm in names:
    v = funcs[nm]
    d[v:v+2] = struct.pack("<H", 0x4770)
    n += 1
print("ephy nops:", n)

for site in (0x477678, 0x477688):  # mml1 assert calls (Gen_Data lines 384/387)
    d[site:site+4] = struct.pack("<HH", 0x2000, 0xBF00)
print("mml1 nops: 2")

for site in (0x305d6, 0x30732, 0x30746, 0x30778, 0x30816, 0x30e08):  # wrevent asserts
    d[site:site+4] = struct.pack("<HH", 0x2000, 0xBF00)
print("wrevent nops: 6")

# fix2: FE01 gate in usim_initialization — resolve by symbol+0x10dc approx:
# the gate = function addr + (0x4f19cc-0x4f08f0) from previous layout; safer: search pattern
# movw r3,#0xfe01; ldrh.w r2,[r4,#1400]; cmp; bne inside usim_initialization
import re
ui = funcs.get("usim_initialization")
print("usim_initialization @", hex(ui))
pat = bytes.fromhex("4ff60163" + "b4f87825")  # movw r3,#fe01; ldrh.w r2,[r4,#1400]
i = bytes(d).find(pat, ui, ui + 5000)
print("gate pattern at:", hex(i) if i >= 0 else "NOT FOUND")
if i >= 0:
    d[i+4:i+8] = bytes.fromhex("4ff60162")  # movw r2,#0xfe01 (replace ldrh)
    print("fix2 applied @", hex(i+4))

open("/tmp/r48-payload.bin", "wb").write(bytes(d))
print("payload sha:", hashlib.sha256(bytes(d)).hexdigest()[:16])

hdr = bytearray(open("/root/MediaTek-HelioX10-Baseband/stock_modem_1_lwg_n.img", "rb").read(64))
struct.pack_into("<I", hdr, 0x3C, len(d))
open("/tmp/r48.img", "wb").write(bytes(hdr) + bytes(d))
print("r48 packed:", 64 + len(d))
