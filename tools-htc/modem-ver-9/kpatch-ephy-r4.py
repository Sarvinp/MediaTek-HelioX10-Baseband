"""Round 4 (generic stub matcher): neutralize EPHY assert stubs by LINE number.
Stub layouts differ (Data_Seq_Type vs Subband variants) but all:
  start with push {r0,r1,r2,lr} = 07 b5
  contain 'movs r2, #line'  = LINE 0x22  within 12 bytes of start
  end with pop {r1,r2,r3,pc} = 0e bd     within 24 bytes of start
Replace [start .. pop+2) with 'bx lr' + NOPs.
"""
import sys

SRC = 'D:/htc-modem/modem-ver-9/pristine-moly.img'
DST = 'D:/htc-modem/modem-ver-9/moly-nosbmipi-r4.img'
LINES = (85, 171, 177)

src = open(SRC, 'rb').read()
d = bytearray(src)

for line in LINES:
    marker = bytes([line, 0x22])
    hits = []
    i = 0
    while True:
        i = d.find(marker, i)
        if i < 0:
            break
        # find push within the 12 bytes before the marker
        for back in range(2, 14, 2):
            start = i - back
            if start >= 0 and d[start:start+2] == b'\x07\xb5':
                # find pop after marker
                end = d.find(b'\x0e\xbd', i, i + 24)
                if end >= 0 and (end + 2 - start) <= 26:
                    hits.append((start, end + 2))
                    break
        i += 1
    # dedupe (same window may be found twice via different marker hits)
    uniq = sorted(set(hits))
    if len(uniq) != 1:
        sys.exit('FATAL: line %d matched %d stubs: %s' % (line, len(uniq), uniq))
    start, stop = uniq[0]
    pad = stop - start - 2
    d[start:stop] = bytes.fromhex('7047') + bytes.fromhex('c046') * (pad // 2)
    print('line %d stub @0x%x (len %d) -> bx lr' % (line, start, stop - start))

assert len(d) == len(src)
open(DST, 'wb').write(bytes(d))
print('wrote %s (%d bytes)' % (DST, len(d)))
