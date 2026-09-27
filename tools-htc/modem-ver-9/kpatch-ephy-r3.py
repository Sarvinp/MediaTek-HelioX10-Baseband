"""Round 3: neutralize BOTH remaining sub-band MIPI assert stubs:
  line 171: EPHY_ErrorCheck_Subband_MipiDataTable
  line 177: EPHY_ErrorCheck_Subband_MipiTpcSectionData
Both fail at sub-band 5 (para1=5). 177 is the last of the 16 EPHY checks.
Each stub = prologue + 'movs r2,#line' + bl + pop (20 bytes) -> bx lr + nops.
Source image: pristine-moly.img (so both patches are applied atomically
against a known-good base).
"""
import sys

SRC = 'D:/htc-modem/modem-ver-9/pristine-moly.img'
DST = 'D:/htc-modem/modem-ver-9/moly-nosbmipi-r4.img'
LINES = (85, 171, 177)
PRO = bytes.fromhex('07b503468de80600')
RPLC = bytes.fromhex('7047') + bytes.fromhex('c046') * 9

src = open(SRC, 'rb').read()
d = bytearray(src)

for line in LINES:
    hits = []
    i = 0
    while True:
        i = d.find(PRO, i)
        if i < 0:
            break
        if d[i+8:i+10] == bytes([line, 0x22]):
            hits.append(i)
        i += 1
    if len(hits) != 1:
        sys.exit('FATAL: line %d stub found %d times' % (line, len(hits)))
    off = hits[0]
    d[off:off+20] = RPLC
    print('line %d stub neutralized at file offset 0x%x' % (line, off))

open(DST, 'wb').write(bytes(d))
print('wrote %s (%d bytes, src %d)' % (DST, len(d), len(src)))
assert len(d) == len(src)
