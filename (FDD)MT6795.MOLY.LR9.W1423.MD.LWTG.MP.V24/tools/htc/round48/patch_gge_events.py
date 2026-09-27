#!/usr/bin/env python3
"""R48: patch l1d_custom_mipi.c event arrays with extracted HTC GGE events."""
import json, re, sys, pathlib

SRC = "/root/MediaTek-HelioX10-Baseband/(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24/custom/modem/l1_rf/MT6795_2G_MT6169_CUSTOM/l1d_custom_mipi.c"
CORPUS = json.load(open(str(pathlib.Path(__file__).parent / "gge_events.json")))

ELM = {0: "GGE_MIPI_NULL", 1: "GGE_MIPI_ASM", 2: "GGE_MIPI_ANT", 3: "GGE_MIPI_PA", 4: "GGE_MIPI_PA_SEC"}
EVT = {0: "GGE_MIPI_EVENT_NULL", 1: "GGE_MIPI_TRX_ON", 2: "GGE_MIPI_TRX_OFF", 3: "GGE_MIPI_TXMID", 4: "GGE_MIPI_TPC_SET"}
BANDS = ["GSM850", "GSM900", "DCS1800", "PCS1900"]
SLOTS = 13
NL = "\r\n"

def emit_rows(rows):
    out = []
    for i, (e, st, sp, ty, tm) in enumerate(rows):
        out.append("         {  /* %2d */  %-15s,  { %3d  , %3d  },  %-18s, %6d       }," % (i, ELM[e], st, sp, EVT[ty], tm))
    for i in range(len(rows), SLOTS):
        out.append("         {  /* %2d */  GGE_MIPI_NULL    ,  {  0  ,  0   },  GGE_MIPI_EVENT_NULL  ,      0       }," % i)
    return NL.join(out)

text = pathlib.Path(SRC).read_bytes().decode("utf-8", errors="replace")

for band in BANDS:
    for kind in ("rx", "tx"):
        key = band + "_" + ("RX" if kind == "rx" else "TX")
        rows = CORPUS[key]
        pat = re.compile(
            "(mipi_" + kind + "ctrl_event\\[\\] \\*/" + NL +
            "      \\{[^" + chr(10) + "]*" + NL +
            "         /[^" + chr(10) + "]*" + NL + ")" +
            "((?:\\s*\\{[^" + chr(10) + "]*\\}," + NL + ")+)" +
            "(      \\},)"
        )
        bstart = text.find("GGE_MIPI_CTRL_TABLE_" + band + "=")
        bend = text.find("sGGE_MIPI_CTRL_TABLE_BAND GGE_MIPI_CTRL_TABLE_", bstart + 10)
        if bend < 0:
            bend = text.rfind("sGGE_MIPIDATA_SUBBAND* GGE_MIPI_CTRL_TABLE_")
        if bend < 0:
            bend = len(text)
        region = text[bstart:bend]
        m = pat.search(region)
        if not m:
            print("PATTERN MISS " + key)
            sys.exit(1)
        new_region = region[:m.start(2)] + emit_rows(rows) + NL + region[m.end(2):]
        text = text[:bstart] + new_region + text[bend:]
        print("patched %s: %d real rows" % (key, len(rows)))

pathlib.Path(SRC).write_bytes(text.encode("utf-8"))
print("l1d_custom_mipi.c written")
