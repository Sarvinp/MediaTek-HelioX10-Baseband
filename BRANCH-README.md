# exp/htc-rf-transplant — MAIN LINE

The full port, Round 1 → Round 52b. Every other branch is a stepping stone that merged or forked into this history. Latest state = latest commit.

## Milestones (newest first)

- **R52/R52b — GGE DATA port**: TX ANT rows 7–11 + RX DATA rows 3–9 from stock (ASM×5+ANT×5, multi-subband ARFCN layouts). R48's GGE events referenced rows that were NULL in our tables = the RFD `0,0,0` NULL-table walk.
- **R51 — UMTS bisect**: 4 port variants, all data-abort; reverted to MOLY-generic UMTS as the stable baseline. `ccci debug=1` proved the DSP FMC table walk never completes (23 min registered, zero RSSI). Next lead: mdlogger EX capture or DSP blob reversing.
- **R50 — Band400 NULL fix + UMTS corpus**: GGE Band400 pointer slots were literal NULL — DSP walk hits them on background PLMN scan → assert. 111 UMTS tables scanned and ported next round.
- **R49 — 🏁 FIRST NETWORK REGISTRATION** on the self-built modem (home PLMN, voice reg state 2, 12-min clean boot). LTE event port + NVRAM assert fixes.
- **R42 — FE01 gate decoded+forced**: `usim_init` gate @`0x4F19C8` requires `ctx+0x578==0xFE01`, written only by `sim_plug_in_ind_handler` — which never runs (broken IND delivery). Forcing it → `mPhbReady=TRUE` first time, PHB gate passed, SIM flow advances to L4C↔SMU security stage.
- **R36–R41 — SIM/UICC chain mapped end-to-end**: `sim_read_req_handler → sim_al_read → … → L1sim → T=0`; `AT+CCHO`→9000; mystery confined to the UST-read → ready-fanout window.
- **R1–R10 — boot + tables**: HTC tail packaging, ePHY assert chain, first MIPI/EVENT table extraction from stock, NVRAM two-path model (image defaults ⊕ stored records), event-vs-data concept, element map (1=ASM 2=ANT 3=PA 4=PA_SEC).

## Open fronts

1. **SIM READY**: EIND fanout (`0x4F1A14`) never fires; `l4csmu_security_req_handler` silent — init aborts between UST read and fanout.
2. **UMTS tables**: port attempts abort; generic tables keep it stable but 3G unproven.
3. **DSP FMC NULL-walk**: late RFD assert on background scan; GGE data rows now real — verify.
4. **Signal bars**: need stable band config + HTC bar/filter code path.

## Conventions

- Commit messages are the lab notebook — full findings + next step in every one. Read `git log` for the real documentation.
- Binary patches that must survive rebuilds get re-implemented in source; `tools-htc/` holds PC-side patchers for image-level work.
- Device flashing = replace `/system/etc/firmware/modem_1_lwg_n.img`, never partition writes.
