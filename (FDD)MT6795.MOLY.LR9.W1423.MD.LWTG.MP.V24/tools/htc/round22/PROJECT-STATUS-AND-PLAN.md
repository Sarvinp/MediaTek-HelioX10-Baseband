# HTC One M9e (himaruhl) — MOLY V24 Port: Full Status & Plan
**Project:** self-built MediaTek MOLY.LR9.W1423.MD.LWTG.MP.V24 modem on MT6795
**Goal:** replace stock HTC firmware with our own build — full function:
no asserts, SIM READY, network registration, signal bars.
**Phone now:** stable on r12c-prod (0 exceptions, USIM detected, SIM NOT_READY)

---

## PART 1 — WHAT WE HAVE DONE (ver-1 … ver-22)

### Phase A: Getting our build to boot at all (ver-1 … ver-6)
- Established build on server 172.16.150.217 (`perl ./make.pl LCSH6795_LWT_L(LWG).mak`)
- Discovered/handled SEC_CCCI signature enforcement: our image must carry
  stock's header + signed tail (legacy wrap method, `make_htc_tail.py`)
- First boots: immediate assert crash loops, exception dumps via dmesg

### Phase B: The MIPI/RF table war (ver-7 … ver-12) — WON
- Assert 1: `mml1_rf_mipi.c` DSP-side MIPI event tables → ported stock's
  LTE event tables into source (26 arrays), rebuilt — assert gone
- Assert 2: `ephy_rf_error_check.c:171` (dev-time RF validation):
  - NVRAM overlay layer found: modem tables = compiled code + NVRAM
    records; EL1A (EL1_CTRL_REG_RW) regenerated as 0xFF garbage →
    source-patched its default to ZERO (R10)
  - My extraction bugs found & fixed en route: R8b TDD TX tables used
    RX clusters (B38/39/40 share ARFCNs); R5/R8b anchors sat +8 high —
    B5/B38 TX actually have 13 rows; event-table pairing corrected
  - Full checker disassembly (R12): flag-gated dev validation of .bss
    runtime composites → gate-off + ARM-veneer `bx lr` (my earlier
    Thumb bytes were an UNDEF in ARM mode — caused type-2 swi crashes)
  - **Result: ephy family CLOSED as dev-validation noise (stock ships it
    off). r12c-prod = 0 exceptions, stable, RF measurements live
    (neighboring-cell requests answered). GGE + UMTS tables transplanted
    binary-side with signature re-anchoring after link shifts.**

### Phase C: The SIM/USIM blocker (ver-13 … ver-22) — IN PROGRESS
- **R18 differential proof:** stock modem on same phone/RIL/card →
  SIM READY, IMSI 432110906760882 (43211), SMS flowing. AP side 100%
  capable; **our image is the sole cause.**
- **R19 transport audit:** every CCCI request class answered correctly
  (GET_SIM_STATUS truthful, APDUs pass — framework even read the ICCID
  through our modem), ccci_fsd healthy, no errors. CCCI is NOT the
  problem. (Also corrected: no READY is "lost" — none is produced.)
- **R20:** all userland AT/log doors closed (atci, pts, ccci_monitor,
  cci_it, ttyC0-3 daemon-owned; mdlogger writes nothing). SIM task =
  prebuilt libsim.a (no source in tree). Stock SIM lib has HTC extras
  ([SIM Q] traces, recovery strings, HIAU board driver) — later shown
  secondary: our lib HAS the recovery machinery.
- **R21 — the UDF-probe bisection (breakthrough method):**
  patch a 2-byte UDF at a function entry in the prod image; boot;
  dmesg `fatal error code 2` = function EXECUTED, silence = never ran.
  Execution map established:

  | SIM init step | Runs? |
  |---|---|
  | card detect / task loop / app start | ✅ |
  | terminal profile download | ✅ |
  | SAT FETCH machinery | ✅ (R18/19 "never FETCHes" was my misread) |
  | STATUS | ✅ |
  | PIN verify (`sim_al_verify_chv`) | ✅ |
  | `sim_select` (EF selection dispatcher) | ❌ NEVER RUNS |
  | `sim_al_select_id` / EF reads / IMSI / READY | ❌ dead |

- **R22 (today):** park point boxed tighter — `sim_select` @0x4E233C
  (53 call sites) never executes; everything upstream through PIN
  verify executes. The stall is in the post-PIN "session ready"
  transition that should trigger the first `sim_select`.

### Corrections log (own errors caught & fixed)
- Thumb `bx lr` in ARM veneers → swi crashes (R10)
- Stale-bin build-order trap → always touch + verify in-bin (R11)
- TDD RX/TX cluster confusion (R11); +8 anchor offset & row truncation (R12)
- "never FETCHes" misread of RIL-proxy APDU status (R21)
- "missing recovery in libsim" (R20→R21: it exists)

---

## PART 2 — THE PLAN (next steps)

### Step 1 (ver-22 continuation): find the dead branch
- Disassemble the verify_chv confirmation handler + the post-PIN state
  logic in `sim_task_main` (0x4E0149) / around app-start caller
  (LR 0x4E0E45). Enumerate the state-machine transition that should
  fire `sim_select` and find the gating condition.
- UDF-probe the intermediate handlers to bisect further (each probe =
  one controlled boot, zero risk to other partitions).

### Step 2: compare with stock at the same site
- Stock is stripped; locate the equivalent code via string anchors
  (e.g. `Bypass Profile Download!`, `SIM_MMRR_READY`, `IMSI_Read`)
  and diff the branch logic. HTC's build (V24_P59, 2508) likely
  handles a case ours doesn't — prime suspect: VERIFY answered with
  `0x91xx` (proactive pending) → stock FETCHes then retries; ours
  parks.

### Step 3: fix (escalating invasiveness)
1. Binary patch (preferred): force the post-PIN transition or accept
   0x91xx on VERIFY + FETCH-retry, on top of r12c-prod
2. Source-level: if the gating lives in tree-owned code, patch & rebuild
3. Fallback: transplant stock's SIM handler region (string-anchored)

### Step 4: validate
- Diag-boot the fixed image (asserts live) → then prod
- Success = SIM READY → IMSI → registration → bars (the original goal)
- Then: signal-bar polish (+ECSQ/HTCSBP already merged in stable branch)

### Risk envelope (unchanged)
- No boot/preloader writes ever; modem swaps only via
  /system/etc/firmware replace + reboot; stock kept as .bak; every
  flash pre-verified byte-level on PC; phone currently on the stable
  known-good image between experiments.

---

**Artifact index:** ver-17/r12c-prod = current best build ·
ver-21/ROUND21-REPORT.md = bisection method & map ·
this file = project-wide status. Server branch: exp/htc-rf-transplant
(commits through 57aa103 + R22 commit).
