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
