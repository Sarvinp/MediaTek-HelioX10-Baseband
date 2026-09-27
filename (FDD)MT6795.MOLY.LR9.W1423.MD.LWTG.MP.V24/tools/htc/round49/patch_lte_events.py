#!/usr/bin/env python3
"""R49 v2: port stock LTE event tables into lte_custom_mipi.c (LF endings)."""
import json, re, pathlib

CORPUS = {t["off"]: t for t in json.load(open(str(pathlib.Path(__file__).parent / "stock_events.json")))}
SRC = "/root/MediaTek-HelioX10-Baseband/(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24/custom/modem/el1_rf/MT6795_LTE_MT6169_CUSTOM/lte_custom_mipi.c"

TX = {"Band1": 0x8A5878, "Band3": 0x8A58B4, "Band5": 0x8AB930, "Band7": 0x8A1364,
      "Band8": 0x8A5878, "Band38": 0x8A3C2C, "Band39": 0x8A1ABC, "Band40": 0x8A4758}
RX = {"Band1": 0x8A7F58, "Band3": 0x8A58B4, "Band5": 0x8ABCE4, "Band8": 0x8A3C2C, "Band39": 0x8A93B4}

ELM = {0: "LTE_MIPI_NULL", 1: "LTE_MIPI_ASM", 2: "LTE_MIPI_ANT", 3: "LTE_MIPI_PA", 4: "LTE_MIPI_PA_SEC"}
EVT = {0: "LTE_MIPI_EVENT_NULL", 1: "LTE_MIPI_TRX_ON", 2: "LTE_MIPI_TRX_OFF", 3: "LTE_MIPI_TPC_SET"}

def emit(rows):
    out = []
    for i, (e, st, sp, ty, tm) in enumerate(rows):
        out.append("   { /* %2d */ %-15s, { %-4d, %-4d }, %-18s, US2OFFCNT(%d) }," % (i, ELM[e], st, sp, EVT[ty], tm // 26))
    return "\n".join(out)

text = pathlib.Path(SRC).read_bytes().decode("utf-8", errors="replace")
NL = "\n"

count = 0
targets = []
for kind, table in (("TX", TX), ("RX", RX)):
    for band, off in table.items():
        targets.append((band, kind, off))

for band, kind, off in targets:
    t = CORPUS.get(off)
    if not t:
        print("MISS corpus", band, kind, hex(off))
        continue
    var = "LTE_%s_MIPI_%s_EVENT" % (band, kind)
    pat = re.compile(
        "(LTE_MIPI_EVENT_TABLE_T " + re.escape(var) + re.escape("[] =") + NL + "\\{)" + NL +
        "((?:.*?\\}," + NL + ")*?)" +
        "(\\};)",
        re.S,
    )
    m = pat.search(text)
    if not m:
        print("PATTERN MISS", var)
        continue
    text = text[:m.end(1)] + NL + emit(t["rows"]) + NL + text[m.start(3):]
    count += 1
    print("patched %s: %d events" % (var, len(t["rows"])))

pathlib.Path(SRC).write_bytes(text.encode("utf-8"))
print("done:", count, "tables")
