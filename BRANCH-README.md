# exp/md-boot-legacy-header

Round 1 packaging experiment — a **documented dead end**, kept for the record.

## Hypothesis (Round 1)
HTC's loader log printed `MD image header size = -1` / `MD image check 188` for stock (a "legacy", CheckHeader-less path), but a different path for images with MOLY's 284-byte V3 CheckHeader. Maybe the modem hung pre-clock *because* of that V3 header.

## What was tried
`tools-htc/strip_checkheader.py` — strips the 284-byte CheckHeader and rewrites the SSSS header length, forcing our image down the stock "legacy" driver path.

## Result
❌ **Invalid experiment.** With the signature kernel patch active the image still took the same load path — and the modem still never executed. The test was also contaminated by a mangled first attempt (zeroed tail bytes). Conclusion: packaging headers were *not* the blocker; the missing piece was the HTC sign tail — proven next in `exp/md-boot-htc-tail`.
