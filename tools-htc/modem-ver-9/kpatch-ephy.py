"""Round 2: neutralize EPHY_ErrorCheck_Subband_MipiDataTable (assert line 171).

The MD now boots (EEEE sign tail package) but asserts 2s after start:
  ephy_rf_error_check.c line=171 para0=1 para1=5 (sub-band idx 5)
The stub is 20 bytes: prologue + 'movs r2,#0xAB' + bl kal_assert_fail_ext + pop.
We replace it with 'bx lr' + nops -> check passes unconditionally.
Only this stub is touched: the prologue+line-byte pattern is unique in the image.
"""
import sys

SRC = 'D:/htc-modem/modem-ver-9/pristine-moly.img'
DST = 'D:/htc-modem/modem-ver-9/moly-nosbmipi.img'

d = bytearray(open(SRC, 'rb').read())

PRO = bytes.fromhex('07b503468de80600')
LINE = 171
END = bytes.fromhex('0ebd')            # pop {r1,r2,r3,pc}
GOOD = bytes.fromhex('07b503468de80600ab22024802490df2bcea0ebd')  # exact stub
RPLC = bytes.fromhex('7047') + bytes.fromhex('c046') * 9  # bx lr + 9*nop (20 bytes)

hits = []
i = 0
while True:
    i = d.find(PRO, i)
    if i < 0:
        break
    if d[i+8:i+10] == bytes([LINE, 0x22]):
        hits.append(i)
    i += 1

if len(hits) != 1:
    sys.exit('FATAL: expected exactly 1 stub for line %d, found %d' % (LINE, len(hits)))

off = hits[0]
assert bytes(d[off:off+20]) == GOOD, 'stub bytes changed: %s' % bytes(d[off:off+20]).hex()
d[off:off+20] = RPLC
assert len(d) == len(open(SRC, 'rb').read()), 'length changed'

open(DST, 'wb').write(bytes(d))
print('patched stub at file offset 0x%x -> bx lr; wrote %s (%d bytes)' % (off, DST, len(d)))
v = open(DST, 'rb').read()
assert v[off:off+2] == b'\x47G'[:2] or v[off:off+2] == bytes.fromhex('4747')
print('verify: stub now:', v[off:off+20].hex())
