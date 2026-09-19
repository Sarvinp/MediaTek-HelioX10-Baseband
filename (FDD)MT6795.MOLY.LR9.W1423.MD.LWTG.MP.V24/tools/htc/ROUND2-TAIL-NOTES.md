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

R2-A TEST RESULT (2026-09-19, executed):
- pristine modem_1_lwg_n.img (8994488B, sha256 d89d839a...) installed, reboot
- kernel: htcfix5 (byte-patch keeps 2015 version string; AUTHEN path proves bypass active)
- [AUTHEN] verify signature FAILED; [SFMT_V2] verify fail (unlock); [SEC_CCCI] verify failed
  -> then sign check success(0x40,0xd4): bypass makes loader CONTINUE after failed verify
- tail signature is body-bound: stock-identical tail bytes do NOT validate MOLY body
- MD image header size = -368773624 (garbage 0xea04f608): kernel does not recognize 64B SSSS
  header as GFH; check 188 -> md check header not exist -> raw load from file offset 0
  -> MD ROM base receives SSSS block, real code at +0xdd
- MD power-on -> immediate ASSERT (exception type 5) -> WDT reset loop, no radio
- verdict: R2-A FAILED. Loader never finds a valid GFH in MOLY image, so entry is wrong
  regardless of kernel bypass. Next: craft proper GFH V3 header for MOLY body (stock-like
  284B header, code at file+0x11C) OR test pristine image on STOCK kernel to isolate
  whether GFH parse differs (stock kernel may accept SSSS-64B).
- stock restored after test: baseband OK, SIM READY, LTE.
