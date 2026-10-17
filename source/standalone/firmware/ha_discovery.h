#ifndef MTTL_HA_DISCOVERY_H
#define MTTL_HA_DISCOVERY_H
#include "settings.h"
#define MTTL_HA_SAMPLE_ENTITIES 25
#define MTTL_HA_SENSOR_COUNT 20
#define MTTL_HA_SENSOR_CHECK_MS 500u
#define MTTL_HA_SENSOR_HEARTBEAT_MS 300000u
#define MTTL_HA_SENSOR_EXPIRE_SECONDS 600u
#define MTTL_HA_ENTITIES 33
/* Full lowercase hexadecimal MAC identity, separate namespace from backend.
 * Bounded JSON output, no credentials. 0 means invalid/capacity failure. */
size_t mttl_ha_discovery(const mttl_settings *,const char *id,unsigned index,char *topic,size_t topic_cap,char *json,size_t json_cap);
int mttl_ha_base(const mttl_settings *,const char *id,char *out,size_t capacity);
#endif
