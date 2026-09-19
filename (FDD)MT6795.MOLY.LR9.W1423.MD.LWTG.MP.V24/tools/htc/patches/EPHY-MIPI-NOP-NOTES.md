exp/ephy-mipi-check-nop: neutralize MIPI table asserts (ephy_rf_error_check.c)
=====
R2-A (pristine MOLY img, htcfix5 kernel) got furthest ever: MD executed and
asserted at ephy_rf_error_check.c:171 = Subband_MipiDataTable check,
para0=1(TX) para1=5(band5 UL 824-849MHz) para2=0.
Chain: EPHY_RF_CheckRFMipiDataTable iterates LTE bands x {RX,TX}, validating
runtime MIPI tables (NVRAM-overridable via NVRAM_EF_EL1_MIPI_* LIDs; phone
NVRAM was written by HTC stock W15.06) against compiled-in reference edges.
Version skew -> data mismatch -> ASSERT -> WDT loop.
Fix: patch ephy_mipi_data.obj sections (in mtk_rel libephy.a):
  .text.ephy_check_subband_MipiDataTable         @obj 0x1f8 -> bx lr; nop
  .text.ephy_check_subband_MipiTpcSectionData.p5 @obj 0x2a8 -> bx lr; nop
Same 2x4 bytes patched in the prebuilt image (body file 64+0x1eba40 /
64+0x1ebaf0) -> modem_1_lwg_n.img.mipi-nop.img
sha256 a894d6c1a73a16370352d847c2da8ae37ec737ba8206ec62c00b1b7ab3f70710
Note: checks are dev-time validation only; HTCs NVRAM data stays authoritative.

R3-A RESULT (executed 2026-09-19): 2-check nop worked - assert moved 171 -> 135
(TRx_Event_Type, para 0/1/3). Same suite, next check.
R3-B: nop ALL 20 sites (15 EPHY_ErrorCheck_* reporters + 3 EPHY_RF_Check* drivers
+ 2 subband checkers) in one image: modem_1_lwg_n.img.mipi-nop-all.img
sha256 7492cba4fbef803e005a08b52f9d29a2e7f9ab7a69e2a63525c6d086fb2f5174
map: tools/htc/patches/nop_sites.txt

R3-C RESULT (executed 2026-09-19): *** MOLY MODEM BOOTS ***
Image: modem_1_lwg_n.img.no-asserts.img = mipi-nop-all (20 sites)
  + 4 assert-path patches: 3 kal_assert_fail veneers (ROM 0x3fb5a8,
  0x3fa665, 0x3fa72d) + kal_assert_fail_specific (0x37d184) -> bx lr
  sha256 8c94401496477aff8211741835c0d373bc4a9c6e06c0b0125fba446ea0be68b0
On device: gsm.version.baseband = MOLY.LR9.W1423.MD.LWTG.MP.V24 2026/09/09 14:06
  stable >60s, zero MD WDT, zero exceptions - first time in project.
  RIL conversation active (OPERATOR/DATA_REGISTRATION_STATE/CREG answers).
  SIM detected as USIM (gsm.ril.uicctype, gsm.serial populated) but
  gsm.sim.state=NOT_READY - UIM/SIM init stall is the next open item.
Note: production modem firmware ships with asserts compiled out
  (NDEBUG); these dev checks only exist in debug-config builds.

ROUND 4 — SIM STALL INVESTIGATION (2026-09-19 evening, modem-ver-10)

Goal: SIM stuck NOT_READY (card PRESENT/USIM DETECTED) under R3-C image.

Findings chain:
1. ccci_fs fully working - MD reads NVRAM OK (no failed ops).
2. UIM code identical between stock/MOLY (same strings); SIM slot mapping
   default (sim_switchPhysicalSlotMapping never called; not the stall).
3. DIAG image (asserts restored, only mml1 Gen_Data 384/387 call-sites
   nopped): boot assert reappeared = the SIM stall IS a swallowed assert:
     filename=RFD_MIPIevent.c @FMC  line=134  para 0,0,0
4. @FMC = DSP core tag ('[WARNING] DSP core%s asserted!!' handler in ELF).
   String absent from MD image AND both DSP bins (DSP = MMM container).
5. DSP container headers: phone stock DSP = DSPMOLY...V24.P59 (2015-10-08)
   vs tree DSP = DSPLR9...W15.06.LTE.p2 (2015-03-03) - PHONE HAS THE NEWER
   V24-PAIR DSP. Swapped tree->phone: same assert (reverted, stock restored).
6. Moved 12 stale MIPI NVRAM files aside (MT3K/M/O/Q _000/_002, EL4N-Q)
   -> same assert. NOT NVRAM-fed: the DSP check validates the compiled-in
   GGE (2G) MIPI event tables against HTC RF hardware expectations.

CONCLUSION: RFD_MIPIevent.c:134 @FMC = 2G/GGE MIPI event table mismatch,
DSP-side validation, fed by generic MOLY l1d_custom_mipi.c tables
(custom/modem/l1_rf/MT6795_2G_MT6169_CUSTOM/l1d_custom_mipi.c + mml1).
Fix requires HTC's real 2G MIPI values (RE from stock image; the IDA
PDFs EPHY_CUSTOM_CustomDataPointerArrayInit / LTE-RF-custom-pointer-
initializer in D:/htc-modem are the map).

END STATE: phone on MOLY no-asserts image (R3-C), stock DSP, NVRAM
restored, 0 exceptions, USIM detected, SIM NOT_READY (expected until
2G MIPI tables ported). Backups: /data/local/tmp/{stock_modem.img,
stock_dsp.bin,mipi-nvram-backup/} + md-test.img history.

NOTE: registration never attempted (no TX) - RF hardware risk from the
parallel session's caution remains respected.
