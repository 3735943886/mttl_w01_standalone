#ifndef MTTL_SDK_SETTINGS_FLASH_H
#define MTTL_SDK_SETTINGS_FLASH_H
#include "settings.h"
int mttl_sdk_settings_load(mttl_settings *);
int mttl_sdk_settings_save(const mttl_settings *);
void mttl_sdk_settings_clock(uint32_t unix_seconds);
void mttl_sdk_settings_status(uint32_t out[4]);
#endif
