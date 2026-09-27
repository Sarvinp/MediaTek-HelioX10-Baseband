#!/usr/bin/env python3
"""R51e: FULL corrected UMTS port: events (RX & TX = ASM{0,1}+ANT{2,5}) + DATA tables.

DATA layout (stock, per band, RX & TX identical): 13 rows:
  0: ASM  port1 REG_W usid ASM0 {freqs..., (0x1C,0x38)}
  1: ASM  port1 REG_W usid ASM0 {..., (0x00,0x11)}   <- RX used (0x00,0x0C) in MOLY; stock=0x11
  2: ANT  port1 REG_W usid ANT0 (0x1C,0x38)
  3: ANT  (0x00,0x00)
  4: ANT  (0x01,0x03)
  5: ANT  (0x02,0x00)
  6-12: null
Band freqs (u32, 100Hz units): B1 19224/19362/19500/19638/19776,
  B2 18524.., B5 8264.., B8 8824.. (read from stock rows).
"""
import json, pathlib, re, struct

CORP = json.load(open(str(pathlib.Path(__file__).parent / "umts_data_corpus.json")))
SRC = "/root/MediaTek-HelioX10-Baseband/(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24/custom/modem/ul1_rf/MT6795_UMTS_FDD_MT6169_CUSTOM/ul1d_custom_mipi.c"

RXMAP = {"UMTSBand1": "RX_UMTSBand1", "UMTSBand2": "RX_UMTSBand2",
         "UMTSBand4": "RX_UMTSBand4", "UMTSBand8": "RX_UMTSBand8"}
TXMAP = {"UMTSBand1": ("TX_BIG", 0), "UMTSBand2": ("RX_0x891f64", 0),
         "UMTSBand4": ("TX_BIG", 28), "UMTSBand8": ("RX_0x894eac", 0)}

ELM = {0: "MIPI_NULL", 1: "MIPI_ASM", 2: "MIPI_ANT", 3: "MIPI_PA", 4: "MIPI_PA_SEC"}

def freqs_of(rows):
    return [r["subs"][0][0] for r in rows[:5] if r["subs"][0][0]] or None

def data_row_str(i, r):
    subs = ", ".join("{ %d ,{0x%02X, 0x%02X}}" % (s[0], s[1] & 0xFFFF, s[2] & 0xFFFF) for s in r["subs"])
    portmap = {2: "UL1_MIPI_PORT1", 3: "UL1_MIPI_PORT0"}
    return "   { /* %2d */ %-9s, %-13s, REG_W     , %-15s, { %s }}," % (
        i, ELM[r["elm"]], portmap.get(r["port"], "UL1_MIPI_PORT1"), "MIPI_USID_%s%d" % (ELM[r["elm"]].replace("MIPI_", ""), 0) if r["elm"] else "MIPI_USID_INIT0", subs)

def null_data_row(i):
    return "   { /* %2d */ %-9s, MIPI_DATA_NULL, SEQ_NULL  , MIPI_USID_INIT0 , { { 0 ,{0x00, 0x00}}, { 0 ,{0x00, 0x00}}, { 0 ,{0x00, 0x00}}, { 0 ,{0x00, 0x00}}, { 0 ,{0x00, 0x00}} }}," % (i, "MIPI_NULL")

def event_rows(total):
    out = []
    rows = [(1, 0, 1, 1, 768), (2, 2, 5, 1, 576)]
    for i in range(total):
        if i < len(rows):
            e, s, sp, ty, o = rows[i]
            out.append("   { /* %2d */ %-9s, { %-4d, %-4d }, %-16s, %-14d }," % (i, ELM[e], s, sp, "MIPI_TRX_ON", o))
        else:
            out.append("   { /* %2d */ %-9s, { %-4d, %-4d }, %-16s, %-14d }," % (i, "MIPI_NULL", 0, 0, "MIPI_EVENT_NULL", 0))
    return out

text = pathlib.Path(SRC).read_bytes().decode("utf-8", errors="replace").replace("\r\n", "\n")
lines = text.split("\n")
out = []
i = 0
ev_n = dat_n = 0
while i < len(lines):
    l = lines[i]
    me = re.match(r"UL1_MIPI_EVENT_TABLE_T UMTS_MIPI_(RX|TX)_EVENT_(UMTSBandNone|UMTSBand\d+)\[", l)
    md = re.match(r"UL1_MIPI_DATA_SUBBAND_TABLE_T UMTS_MIPI_(RX|TX)_DATA_(UMTSBandNone|UMTSBand\d+)\[", l)
    if l.rstrip().endswith("= {{0}};") or (me and "[" not in l.split("[", 1)[1]):
        out.append(l)
        i += 1
        continue
    if me or md:
        m = me or md
        kind, band = m.group(1), m.group(2)
        out.append(l)
        i += 1
        while i < len(lines) and lines[i].strip() != "{" and lines[i].strip().rstrip("[") != "":
            # for DATA tables the header comment lines follow; keep until '{' line
            out.append(lines[i])
            i += 1
            if i < len(lines) and lines[i].strip() == "{":
                break
        if i < len(lines) and lines[i].strip() == "{":
            out.append(lines[i])
            i += 1
        body = []
        while i < len(lines) and lines[i].strip() != "};":
            body.append(lines[i])
            i += 1
        if me:
            total = 24 if kind == "RX" else 16
            if band == "UMTSBandNone":
                out.extend(body)  # keep null
            else:
                out.extend(event_rows(total))
                ev_n += 1
        else:
            key = None
            if kind == "RX" and band in RXMAP:
                rows = CORP[RXMAP[band]]
                key = True
            elif kind == "TX" and band in TXMAP:
                tkey, off = TXMAP[band]
                rows = CORP[tkey][off:off + 13]
                key = True
            if key and band != "UMTSBandNone":
                # find last non-null stock row
                nn = max((k + 1 for k in range(len(rows)) if rows[k]["elm"]), default=0)
                for k in range(nn):
                    out.append(data_row_str(k, rows[k]))
                for k in range(nn, 28 if kind == "RX" else 18):
                    out.append(null_data_row(k))
                dat_n += 1
            else:
                out.extend(body)
        continue
    out.append(l)
    i += 1

pathlib.Path(SRC).write_bytes("\r\n".join(out).encode())
print("events patched:", ev_n, "data tables patched:", dat_n)
