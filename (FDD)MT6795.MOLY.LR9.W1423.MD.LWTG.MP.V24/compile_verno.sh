#!/bin/bash
set -e
# 1. Setup Environment
export PATH=$(pwd)/tools/GCC/4.6.2/linux/bin:$PATH
export COMPILER_PATH=$(pwd)/tools/GCC/4.6.2/linux/bin

# 2. Cleanup and Preparation
mkdir -p build/LCSH6795_LWT_L/LWG/bin/obj/verno
rm -f build/LCSH6795_LWT_L/LWG/bin/obj/verno/verno.obj

# 3. Compile verno.c (Single continuous command)
arm-none-eabi-gcc -mthumb \
@./build/LCSH6795_LWT_L/LWG/bin/via/verno.via \
@./build/LCSH6795_LWT_L/LWG/bin/via/verno_inc.via \
-c -Wno-attributes -Wno-pragmas -fcommon -march=armv7-r -mcpu=cortex-r4 \
-mlittle-endian -Wa,-mimplicit-it=always -mabi=aapcs -Os -fno-strict-aliasing \
-fno-exceptions -ffunction-sections -fdata-sections -Wall -mno-unaligned-access \
-fshort-wchar -o ./build/LCSH6795_LWT_L/LWG/bin/obj/verno/verno.obj \
build/LCSH6795_LWT_L/LWG/verno/verno.c

echo "Compilation successful: $(ls -l build/LCSH6795_LWT_L/LWG/bin/obj/verno/verno.obj)"
