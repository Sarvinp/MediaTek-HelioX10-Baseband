Round 2: HTC MD tail splice experiment
=====
Kernel log (htcfix5): signature_check offset:64, tail:148 — CCCI reads the
last 148 bytes of the MD image. Stock tail = 60B signature + 4x EEEE
region-descriptor table (regions 01/02/06, size 0x19080) + 0xffffffff end
marker. MOLY-built tail = zeros + LWG/version strings, no EEEE table.
Experiment: graft stock tail onto MOLY body (PC: modem-ver-9/tools).
Artifact: modem_1_lwg_n.img.htc-tail.img sha256 355f38ca74b45b32...
Test: copy to /system/etc/firmware/modem_1_lwg_n.img under boot-htcfix5,
watch for CLDMA clock-on vs pre-clock hang.
CORRECTION after ELF/tail analysis:
- pristine MOLY img framing is correct (64B SSSS hdr + ROM body + 148B tail)
- pristine tail is BYTE-IDENTICAL to stock tail (incl. signature blob) -> tail transplant moot
- round-1 legacy image was mangled (zeroed tail; header parse fell to offset-0 load;
  MD booted into the SSSS block) -> pre-clock hang was self-inflicted
- modem-ver-7 stock ELF is actually a MOLY V24 build (0 symbol diff) - discarded
- next: test pristine image as-is on stock kernel (R2-A)
