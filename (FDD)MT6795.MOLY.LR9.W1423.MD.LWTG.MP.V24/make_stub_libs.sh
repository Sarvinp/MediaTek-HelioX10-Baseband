#!/bin/bash
set -e
CC=tools/GCC/4.6.2/linux/bin/arm-none-eabi-gcc
AR=tools/GCC/4.6.2/linux/bin/arm-none-eabi-ar
DIR=build/LCSH6795_LWT_L/LWG/bin/lib
TMP=build/LCSH6795_LWT_L/LWG/stub_libs
mkdir -p "$DIR" "$TMP"

make_lib() {
  lib="$1"
  shift
  c="$TMP/$lib.c"
  o="$TMP/$lib.o"
  : > "$c"
  for sym in "$@"; do
    printf 'int %s(void) { return 0; }\n' "$sym" >> "$c"
  done
  "$CC" -mthumb -march=armv7-r -mcpu=cortex-r4 -mlittle-endian -mabi=aapcs -Os -c "$c" -o "$o"
  "$AR" rcs "$DIR/lib$lib.a" "$o"
}

make_lib dtmf DTMF_SetKey DTMF_Tone DTMF_Gen DTMF_GetBufferSize DTMF_Init
make_lib g711 G711_Enc_Set_Handle G711_Dec_Set_Handle
make_lib g722 G722_Enc_Set_Handle G722_Dec_Set_Handle
make_lib g7231 G7231_Enc_Set_Handle G7231_Dec_Set_Handle
make_lib g726 G726_Enc_Set_Handle G726_Dec_Set_Handle
make_lib g729 G729_Enc_Set_Handle G729_Dec_Set_Handle
make_lib sss_gcc_dummy SST_Get_ChipRID SSS_Init_Crypto_Drv
"$AR" rcs "$DIR/libg711plc.a"
"$AR" rcs "$DIR/libkdf.a"
