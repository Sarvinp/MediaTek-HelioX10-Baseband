#!/usr/bin/env python3
"""R39d: apply 18 ephy checker nops BY SYMBOL NAME at EVEN addresses.
Run AFTER full build; patches the .bin in place."""
import subprocess, struct

ELF = "build/LCSH6795_LWT_L/LWG/bin/LCSH6795_LWT_L_MDBIN_PCB01_MT6795_S00.elf"
BIN = "build/LCSH6795_LWT_L/LWG/bin/LCSH6795_LWT_L_MDBIN_PCB01_MT6795_S00.MOLY_LR9_W1423_MD_LWTG_MP_V24.bin"
names=["EPHY_ErrorCheck_Data_Seq_Type","EPHY_ErrorCheck_SubFreq_Lower_Bound","EPHY_ErrorCheck_SubFreq_Upper_Bound",
"EPHY_ErrorCheck_SubFreq_Zero","EPHY_ErrorCheck_SubFreq_Max","EPHY_ErrorCheck_TPC_Data_Num","EPHY_ErrorCheck_IMM_Data_Num",
"EPHY_ErrorCheck_TPC_ELM_Type","EPHY_ErrorCheck_TRx_Event_Type","EPHY_ErrorCheck_TRx_Event_Data_Num",
"EPHY_ErrorCheck_TPC_Event_Data_Num","EPHY_ErrorCheck_MAX_Event_Data_Num","EPHY_RF_CheckSplitIndTable",
"EPHY_RF_CheckRFMipiDataTable","EPHY_RF_CheckRFMipiBypassDataTable","ephy_check_subband_MipiDataTable",
"ephy_check_subband_MipiTpcSectionData.part.5","EPHY_ErrorCheck_Subband_MipiTpcSectionData"]
syms = subprocess.run(["readelf","-sW",ELF],capture_output=True,text=True).stdout
funcs={}
for l in syms.splitlines():
    p=l.split()
    if len(p)>=8 and p[3]=="FUNC":
        try: funcs.setdefault(p[7], int(p[1],16))
        except: pass
d=bytearray(open(BIN,"rb").read())
for n in names:
    v = funcs[n] & ~1   # strip Thumb bit: EVEN address required
    d[v:v+2]=struct.pack("<H",0x4770)
    print(f"nop {hex(v)} {n}")
open(BIN,"wb").write(bytes(d))
print("done: 18 nops applied at even addresses")
