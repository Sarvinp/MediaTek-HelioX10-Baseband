#!/usr/bin/env python3
"""Splice the HTC stock MD tail (last 148 bytes) onto a MOLY-built modem image.

Why: the MT6795 CCCI loader reads the last 148 bytes of the MD image
(kernel log: "signature_check offset:64, tail:148"). The stock tail carries
a 4x 'EEEE' region-descriptor table + signature blob that the loader/MPU
path consumes; MOLY-built images have a zeroed tail there. Round-2 boot
experiment: graft the stock tail onto the MOLY body byte-for-byte.

Usage: make_htc_tail.py <moly_img> <stock_img> <out_img>
"""
import sys
import hashlib
import pathlib

TAIL = 148


def main() -> None:
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    moly_p, stock_p, out_p = (pathlib.Path(p) for p in sys.argv[1:4])
    m = moly_p.read_bytes()
    s = stock_p.read_bytes()

    if b"EEEE" not in s[-TAIL:]:
        sys.exit("stock tail does not contain an EEEE table - wrong stock image?")
    if b"EEEE" in m[-TAIL:]:
        sys.exit("moly image already has an EEEE tail - nothing to splice")

    img = m[:-TAIL] + s[-TAIL:]
    assert len(img) == len(m), "size must be preserved"
    out_p.write_bytes(img)

    print(f"wrote {out_p} ({len(img)} bytes)")
    print(f"sha256      : {hashlib.sha256(img).hexdigest()}")
    print(f"body==moly : {img[:-TAIL] == m[:-TAIL]}")
    print(f"tail==stock: {img[-TAIL:] == s[-TAIL:]}")


if __name__ == "__main__":
    main()
