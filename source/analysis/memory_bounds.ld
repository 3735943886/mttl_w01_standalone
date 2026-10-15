/* Offline extra linker constraints. No image generation or boot validation. */
/* Keep the SDK's original TCM heap at its original address. Reserve only
 * the following tail before the bounded newlib allocator starts. */
SECTIONS {
  .mttl_cache __tcm_bss_end__ (NOLOAD) : { *(.mttl.cache) } > TCM
}
__mttl_newlib_start = ALIGN(MAX(__tcm_bss_end__, ADDR(.mttl_cache) + SIZEOF(.mttl_cache)), 8);
__mttl_newlib_limit = 0x20000000;
__mttl_msp_limit = 0x1006F000;
__mttl_msp_top = 0x10070000;
ASSERT(__mttl_newlib_start <= __mttl_newlib_limit, "TCM allocator has no space")
ASSERT(__HeapLimit <= __mttl_msp_limit, "application overlaps reserved MSP budget")
