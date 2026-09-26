#!/usr/bin/env python3
"""R40 v3: validate MIPI event index ranges vs data row counts (robust CRLF handling)."""
import re, sys

SRC = sys.argv[1] if len(sys.argv) > 1 else "/root/MediaTek-HelioX10-Baseband/(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24/custom/modem/el1_rf/MT6795_LTE_MT6169_CUSTOM/lte_custom_mipi.c"
src = open(SRC, encoding="utf-8", errors="replace").read()
# normalize newlines but keep content
src = src.replace("\r\n", "\n").replace("\r", "\n")

report, bad = [], []
for kind in ("TX", "RX"):
    ev_pat = r"LTE_MIPI_EVENT_TABLE_T\s+(LTE_Band\w+_MIPI_" + kind + r"_EVENT)\s*\[\s*\]\s*=\s*\{(.*?)\n\};"
    dt_pat = r"LTE_MIPI_DATA_SUBBAND_TABLE_T\s+(LTE_Band\w+_MIPI_" + kind + r"_DATA)\s*\[\s*\]\s*=\s*\{(.*?)\n\};"
    evs = dict(re.findall(ev_pat, src, re.S))
    dts = dict(re.findall(dt_pat, src, re.S))
    print(f"== {kind}: {len(evs)} event tables, {len(dts)} data tables ==")
    for name, body in sorted(evs.items()):
        pairs = re.findall(r"\{ /\* \d+\s*\*/\s*LTE_MIPI_(\w+),\s*\{\s*(\d+)\s*,\s*(\d+)\s*\}", body)
        real = [(e, int(a), int(b)) for e, a, b in pairs if e != "NULL"]
        dname = name.replace("_EVENT", "_DATA")
        dbody = dts.get(dname)
        nrows = len(re.findall(r"\{ /\* \d+\s*\*/", dbody)) if dbody is not None else -1
        if real:
            mx = max(max(a, b) for _, a, b in real)
            st = "OK" if nrows > mx else "OOB!"
        else:
            mx = "-"
            st = "NULL-only"
        line = f"{name:42s} datarows={nrows:3d} maxidx={mx} {st}"
        report.append(line)
        if st == "OOB!":
            bad.append(line)
print()
print("\n".join(report))
print()
print("PROBLEMS:" if bad else "ALL INDEX RANGES OK")
print("\n".join(bad))
