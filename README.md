# HTC One M9e (himaruhl) · MOLY V24 Modem Port

**Goal:** make a self-built MediaTek MOLY LR9.W1423 MD LWTG MP V24 modem (built from this source tree) run on the HTC One M9e (MT6795 Helio X10), replacing the stock HTC modem image — boot, SIM, network registration, and eventually signal bars.

This fork is the working history of that port: **75+ commits across 6 branches**, from "image won't even load" to **first network registration on the self-built modem** (Round 49).

## What was the problem?

The MOLY source tree is a *generic* MediaTek MT6795 modem. The HTC device expects:

- its own image packaging (SSSS header + 148-byte `EEEE` sign tail) — without it the modem never leaves reset
- a kernel-side signature check (`SEC_CCCI`) that rejects non-HTC images — bypassed by a boot kernel patch
- HTC's RF configuration: MIPI/event/data/PA tables per RAT (GGE 2G, UMTS 3G, LTE 4G) matched to the phone's transceiver + front-end hardware
- HTC-specific SIM/USIM behavior (vendor AT commands, PHB readiness gate, indication delivery)

## What works on the self-built modem today

- ✅ Image loads and the modem **boots stably** (HTC tail packaging solved)
- ✅ CCCI/CLDMA AP↔MD communication operational
- ✅ SIM I/O works (`AT+CCHO` / OpenChannel → `9000`)
- ✅ **Network registration achieved** (home PLMN, voice reg state 2 — Round 49)
- ✅ LTE + GGE event/data tables ported from stock; DSP-side FMC assert fixed
- ⏳ Open: SIM never reaches full READY (EIND fanout blocked), UMTS tables abort (bisected, reverted to generic), signal bars unstable, one late DSP NULL-table walk under investigation

## Branches

| Branch | What it is |
|---|---|
| `master` | Upstream baseline, untouched + this README |
| `fix/linux-build-nvram-cgen-link` | Make the 2015 tree build on a modern Linux host (toolchain sections, `-fno-common`, NVRAM cgen link) |
| `stable/htc-moly-cgmr-atcmd` | First stable build: fixes `+CGMR` format-string crash in `libl4.a`, adds 6 HTC vendor AT commands. Tag: `htc-moly-stable-v1` |
| `exp/md-boot-legacy-header` | Round 1 packaging experiment (strip CheckHeader) — documented dead end |
| `exp/md-boot-htc-tail` | **The boot breakthrough**: graft the stock 148-byte EEEE tail onto the MOLY image → modem first boots on device |
| `exp/ephy-mipi-check-nop` | Neutralize the 16 ePHY RF validation asserts → stable boot, no watchdog reset; analysis of the swallowed DSP assert |
| `exp/htc-rf-transplant` | **Main line (R1→R52b)**: RF tables transplanted from stock (GGE/UMTS/LTE), FE01 SIM gate decoded+forced, first registration, UMTS bisects, DSP FMC NULL-walk diagnosis |

Each branch carries a `BRANCH-README.md` with its own details.

## Method

Analyze → Map → Trace → Verify → Reproduce → Modify. Every round: patch source or binaries, rebuild on the build server, flash by replacing `/system/etc/firmware/modem_1_lwg_n.img` (stock kept as `.bak`), read `dmesg`/kmsg/AEE asserts, commit with a full findings message. Kernel-side signature bypass lives in a patched boot image (`boot-htcfix5`) on the device, not in this repo.

## Hardware / setup

- Device: HTC One M9e `himaruhl`, MT6795 Helio X10, Magisk-rooted
- Build: this tree on a Linux build server (`make.sh`, ARM GCC 4.6-era toolchain)
- Modem: MT6169 transceiver, Cortex-R4 MD core + DSP/FMC core
- Flash target: `/system/etc/firmware/modem_1_lwg_n.img` (file replace, no partition flashing)

## Credits

Original source dump: upstream of this fork (2015 MediaTek GPL drop).
Port work: Sarvinp (see branch histories).

License: GPL-2.0 (as upstream).
