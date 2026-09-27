"""Round 6: r4 (EPHY 85/171/177) + MIPI 387 + EPHY line 135 (TRx_Event_Type).
All four EPHY stubs via generic line matcher; MIPI387 via NOP patch."""
import hashlib
import sys

SRC = 'D:/htc-modem/modem-ver-9/pristine-moly.img'
DST = 'D:/htc-modem/modem-ver-9/moly-r6.img'
EPHY_LINES = (85, 135, 171, 177)
MIPI387_OFF = 0x4776aa

src = open(SRC, 'rb').read()
d = bytearray(src)

for line in EPHY_LINES:
    marker = bytes([line, 0x22])
    hits = []
    i = 0
    while True:
        i = d.find(marker, i)
        if i < 0:
            break
        for back in range(2, 14, 2):
            start = i - back
            if start >= 0 and d[start:start+2] == b'\x07\xb5':
                end = d.find(b'\x0e\xbd', i, i + 24)
                if end >= 0 and (end + 2 - start) <= 26:
                    hits.append((start, end + 2))
                    break
        i += 1
    uniq = sorted(set(hits))
    if len(uniq) != 1:
        sys.exit('FATAL: line %d matched %d' % (line, len(uniq)))
    start, stop = uniq[0]
    pad = stop - start - 2
    d[start:stop] = bytes.fromhex('7047') + bytes.fromhex('c046') * (pad // 2)
    print('EPHY line %d -> 0x%x' % (line, start))

orig = bytes(d[MIPI387_OFF:MIPI387_OFF+10])
if orig != bytes.fromhex('40f28312034983f79aef'):
    sys.exit('FATAL: mipi387 bytes %s' % orig.hex())
d[MIPI387_OFF:MIPI387_OFF+10] = bytes.fromhex('00bf') * 5
print('MIPI 387 -> NOPs @0x%x' % MIPI387_OFF)

open(DST, 'wb').write(bytes(d))
print('wrote %s md5 %s' % (DST, hashlib.md5(bytes(d)).hexdigest()))
