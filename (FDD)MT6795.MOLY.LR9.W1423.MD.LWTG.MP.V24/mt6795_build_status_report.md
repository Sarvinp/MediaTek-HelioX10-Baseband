# MediaTek MT6795 Build Status Report

## 1. Executive Summary

This report summarizes the current status of compiling the MediaTek MT6795 MOLY baseband firmware:

```
(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24
```

The project has successfully progressed from initial environment and toolchain failures into active code generation and module processing stages on the Linux build server.

Major progress has been achieved:

- Linux host environment stabilized
- ARM GCC toolchain path resolved
- `nvram_auto_gen` linker/header failures resolved
- `kal_public_api.h` compatibility issue corrected
- Full dependency scanning and module generation now execute successfully
- Build now advances into the `Cgen` phase

The current remaining blocker is now isolated to a later-stage `Cgen` execution issue caused by Windows CRLF line endings inside the `tools/Cgen` script.

---

## 2. Current Host Environment Status

### Windows Environment (Local Machine)

Path Checked:

```
D:\htc-modem\MediaTek-HelioX10-Baseband\
(FDD)MT6795.MOLY.LR9.W1423.MD.LWTG.MP.V24
```

Local Toolchain verified:

```
tools\GCC\4.6.2\win\bin\arm-none-eabi-gcc.exe
```

Windows build attempt fails with:

```
[Error:] Target build on Windows is not avaliable,
please use the linux server to build Target!!
```

Conclusion: Windows can only be used for configuration tasks. Final firmware compilation must occur on Linux.

---

## 3. Linux Build Environment

Host OS:

```
Ubuntu 22.04 LTS (amd64)
```

Environment repairs performed:

- Fixed package inconsistencies
- Repaired PATH environment
- Verified native GCC
- Verified ARM cross‑compiler execution

ARM toolchain in use:

```
/opt/gcc-arm-none-eabi-4_6-2012q4/bin/arm-none-eabi-gcc
```

---

## 4. Project Build Targets

Located in the `make/` directory:

FDD LTE target:

```
make/LCSH6795_LWT_L(LWG).mak
```

TDD LTE target:

```
make/LCSH6795_LWT_L(LTTG).mak
```

The current work focuses on the FDD configuration.

---

## 5. Major Issues Resolved

### GCC Compatibility (`-fcommon`)

Modern GCC versions changed global symbol handling which conflicted with legacy MediaTek source assumptions.

Actions performed:

- Added `-fcommon` support in GCC build flags
- Removed conflicting `-fno-common` occurrences

Result:

```
Legacy global variable linkage restored.
```

---

### `nvram_auto_gen` Duplicate Symbol Failure

Original error:

```
make: *** [make/Codegen.mak:894: nvram_auto_gen.det] Error 2
```

Root cause:

Duplicate inline helper functions defined across multiple translation units when building host tools.

Affected symbols:

```
kal_mem_cpy
kal_mem_set
kal_mem_cmp
kal_mem_bwcpy
kal_query_boot_mode
stack_timer_get_remaining_time
```

Fix applied in:

```
interface/service/kal/kal_public_api.h
```

Changes included:

- Host‑side macros for memory functions
- Stub implementations for runtime‑dependent helpers
- Removal of duplicate inline blocks after `#endif /* NVRAM_AUTO_GEN */`

Verification:

```
./make.sh nvram_auto_gen LCSH6795_LWT_L
```

Result: successful completion without linker errors.

---

## 6. Build Progress

The build now completes multiple generation phases successfully.

Subsystem generation includes:

```
Generate asn1_common information
Generate audio information
Generate ccci information
Generate config information
Generate custom information
Generate drv information
Generate media information
Generate nvram information
Generate sys_drv information
Generate verno information
```

Dependency scanning confirms successful loading of internal tooling such as:

```
tools/sys_auto_gen.pl
tools/sysGen1.pl
tools/sysGen2.pl
tools/scatGen.pl
tools/ldsGenLib.pl
tools/FileInfoParser.pm
tools/sysGenUtility.pm
tools/CommonUtility.pm
tools/config_MemSegment.pm
tools/scatInfo.pm
tools/ldsInfo.pm
tools/pack_dep_gen.pm
```

Final generation messages observed:

```
Generate config information
genmoduleinfo is done.
Generating .lis and .def files are done
```

---

## 7. Current Build Failure

The build now stops during the Codegen stage:

```
Error: Cgen failed.
Please check ./build/LCSH6795_LWT_L/LWG/bin/log/codegen.log
```

Direct runtime error:

```
/bin/bash: ./tools/Cgen: /bin/bash^M: bad interpreter: No such file or directory
```

---

## 8. Root Cause

The script `tools/Cgen` contains Windows CRLF line endings.

Linux interprets the shebang as:

```
#!/bin/bash^M
```

which causes execution failure.

---

## 9. Required Fix

Convert the script to Unix format.

Recommended command:

```
sed -i 's/\r$//' tools/Cgen
chmod +x tools/Cgen
```

Alternative method:

```
dos2unix tools/Cgen
chmod +x tools/Cgen
```

After correction, rebuild using:

```
./make.sh "LCSH6795_LWT_L(LWG).mak" new
```

---

## 10. Current Build State Summary

| Component | Status |
|----------|--------|
| Linux environment | Stable |
| ARM toolchain | Working |
| Toolchain path | Fixed |
| nvram_auto_gen | Fixed |
| kal_public_api.h compatibility | Fixed |
| GCC compatibility flags | Fixed |
| System generation | Working |
| Module generation | Working |
| Cgen stage | Failing |
| Current blocker | CRLF in tools/Cgen |

---

## 11. Overall Assessment

The project has advanced significantly beyond the original build failures.

Key build subsystems including NVRAM generation, module generation, and configuration generation are now functioning.

The remaining failure is isolated to a script formatting issue and is considered a low‑complexity fix.

Once the CRLF issue in `tools/Cgen` is corrected, the build should proceed to the next compilation stages.


---

# 13. Latest Build Progress Update

Additional progress has been confirmed after the previous report.

## 13.1 `nvram_auto_gen` Fully Fixed

The earlier `nvram_auto_gen` failures caused by:

- duplicate symbol handling
- GCC compatibility issues
- legacy inline definitions
- host-side header conflicts

have now been fully resolved.

The build successfully completes the NVRAM generation stage without linker or compilation failures.

---

## 13.2 `Cgen` CRLF Issue Fixed

The previous failure:

```text
/bin/bash: ./tools/Cgen: /bin/bash^M: bad interpreter
```

was caused by Windows CRLF (`
`) line endings inside the `tools/Cgen` script.

This issue was resolved by converting the script to Unix LF format.

Example fix:

```bash
sed -i 's/\r$//' tools/Cgen
chmod +x tools/Cgen
```

After conversion, the `Cgen` stage executes correctly under Linux.

---

## 13.3 Build Reached Final Link Stage

Following the earlier fixes:

- GCC compatibility corrections
- `kal_public_api.h` host-build adjustments
- `-fcommon` restoration
- `Cgen` repair

the firmware build now progresses through:

- dependency generation
- code generation
- NVRAM generation
- EMI generation
- module processing
- scatter/link preparation
- object compilation

and successfully reaches the final firmware link stage.

This indicates that the overall build system, compiler integration, and generation pipeline are now functioning correctly.

---

## 13.4 Current Remaining Failure

The remaining build failure now occurs only during final linking.

Root cause:

```text
Required static library (.a) files are missing.
```

The linker cannot complete firmware image generation because one or more prebuilt MediaTek archive libraries are absent from the source tree or build output.

Typical missing components may include:

```text
*.a
```

from:

```text
build/.../lib/
module/.../
custom/.../
```

This is no longer a compiler, host-environment, or code-generation problem.

The remaining issue is now strictly related to unavailable prebuilt binary library dependencies.

---

# 14. Updated Overall Assessment

The MT6795 modem firmware build has advanced significantly:

- Linux environment stabilized
- legacy GCC compatibility repaired
- NVRAM generation repaired
- Cgen execution repaired
- full compile pipeline operational
- final firmware link reached

At the current stage, the build infrastructure itself is considered operational.

The only remaining blocker is the absence of required proprietary/static `.a` libraries needed by the final linker stage.
