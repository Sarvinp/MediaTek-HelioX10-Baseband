#!/usr/bin/env python3
"""R50 v2: port stock UMTS event tables into ul1d_custom_mipi.c (line parser)."""
import pathlib
import re

SRC = "/root/MediaTek-HelioX10-Baseband/(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24/custom/modem/ul1_rf/MT6795_UMTS_FDD_MT6169_CUSTOM/ul1d_custom_mipi.c"

RX = [(1, 0, 1, 1, 768), (2, 2, 5, 1, 576)]
TX = [(3, 0, 0, 1, 76), (3, 1, 4, 2, 38), (1, 5, 6, 1, 768), (2, 7, 10, 1, 576)]
ELM = {0: "MIPI_NULL", 1: "MIPI_ASM", 2: "MIPI_ANT", 3: "MIPI_PA", 4: "MIPI_PA_SEC"}
EVT = {0: "MIPI_EVENT_NULL", 1: "MIPI_TRX_ON", 2: "MIPI_TRX_OFF", 3: "MIPI_TPC_SET"}


def emit(rows, total):
    out = []
    for i in range(total):
        if i < len(rows):
            e, s, sp, ty, o = rows[i]
            out.append("   { /* %2d */ %-9s, { %-4d, %-4d }, %-16s, %-14d }," % (i, ELM[e], s, sp, EVT[ty], o))
        else:
            out.append("   { /* %2d */ %-9s, { %-4d, %-4d }, %-16s, %-14d }," % (i, "MIPI_NULL", 0, 0, "MIPI_EVENT_NULL", 0))
    return out


raw = pathlib.Path(SRC).read_bytes()
text = raw.decode("utf-8", errors="replace")
crlf = "\r\n" in text
lines = text.replace("\r\n", "\n").split("\n")

count = 0
out_lines = []
i = 0
while i < len(lines):
    m = re.match(r"UL1_MIPI_EVENT_TABLE_T UMTS_MIPI_(RX|TX)_EVENT_(UMTSBandNone|UMTSBand\d+)\[", lines[i])
    if m:
        kind = m.group(1)
        total = 24 if kind == "RX" else 16
        rows = RX if kind == "RX" else TX
        out_lines.append(lines[i])
        i += 1
        while i < len(lines) and lines[i].strip() != "{":
            out_lines.append(lines[i])
            i += 1
        if i < len(lines):
            out_lines.append(lines[i])
            i += 1
        body = []
        while i < len(lines) and lines[i].strip() != "};":
            body.append(lines[i])
            i += 1
        if len("".join(body)) < 30:  # {0} one-liner style, keep as-is
            out_lines.extend(body)
        else:
            out_lines.extend(emit(rows, total))
            count += 1
            print("patched", m.group(2), kind)
        continue
    out_lines.append(lines[i])
    i += 1

nl = "\r\n" if crlf else "\n"
pathlib.Path(SRC).write_bytes(nl.join(out_lines).encode())
print("done:", count, "(crlf:", crlf, ")")
