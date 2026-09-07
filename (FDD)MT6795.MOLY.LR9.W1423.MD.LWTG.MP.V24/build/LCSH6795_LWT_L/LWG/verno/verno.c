#include "kal_public_api.h"
#if defined(__MTK_TARGET__)
__attribute__ ((section ("RELEASE_VERNO_RW"))) static kal_char verno_str[] = "MOLY.LR9.W1423.MD.LWTG.MP.V24";
__attribute__ ((section ("BUILD_TIME_RW"))) static kal_char build_date_time_str[] = "2026/07/11 15:42";
__attribute__ ((section ("RELEASE_BRANCH_RW"))) static kal_char build_branch_str[] = "LR9.W1423.MD.LWTG.MP LCSH6795_LWT_L";
extern kal_uint32 RELEASE_VERNO_RW$$Base;
extern kal_uint32 BUILD_TIME_RW$$Base;
extern kal_uint32 RELEASE_BRANCH_RW$$Base;
#endif

kal_char* release_verno(void)
{
#if defined(__MTK_TARGET__)
#if defined(__GNUC__)
   return verno_str;
#else
   return (kal_char*)&RELEASE_VERNO_RW$$Base;
#endif
#else
   static kal_char verno_str[] = "MOLY.LR9.W1423.MD.LWTG.MP.V24";
   return verno_str;
#endif
}

kal_char* release_hal_verno(void)
{
   static kal_char hal_verno_str[] = "";
   return hal_verno_str;
}

kal_char* release_hw_ver(void)
{
   static kal_char hw_ver_str[] = "LCSH6795_LWT_L_HW";
   return hw_ver_str;
}

kal_char* build_date_time(void)
{
#if defined(__MTK_TARGET__)
#if defined(__GNUC__)
   return build_date_time_str;
#else
   return (kal_char*)&BUILD_TIME_RW$$Base;
#endif
#else
   static kal_char build_date_time_str[] = "2026/07/11 15:42";
   return build_date_time_str;
#endif
}

kal_char* release_build(void)
{
   static kal_char build_str[] = "BUILD_NO";
   return build_str;
}

kal_char* release_branch(void)
{
#if defined(__MTK_TARGET__)
#if defined(__GNUC__)
   return build_branch_str;
#else
   return (kal_char*)&RELEASE_BRANCH_RW$$Base;
#endif
#else
   static kal_char build_branch_str[] = "LR9.W1423.MD.LWTG.MP LCSH6795_LWT_L";
   return build_branch_str;
#endif
}

kal_char* release_flavor(void)
{
   static kal_char build_flavor_str[] = "LWG";
   return build_flavor_str;
}

