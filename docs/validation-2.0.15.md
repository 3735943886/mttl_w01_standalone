# 2.0.15 validation

Build: `552f007895f9d4f0`; firmware SHA-256: `2675c5fe4e714023887f7ededbceb56b2338a7178eedfdf9eb270828e7fa9ffc`.

- Portable ARM core/integration: 2099 checks passed. All 33 Discovery JSON objects validated.
- Current SDK ELF sensor publication: 311 checks passed; twenty topics, exact payloads, duplicate suppression, 300s heartbeat, stale-data rejection, queue rejection and uptime wrap.
- Current SDK ELF regressions: remaining-time packets 122, timers/settings 158, HA timer/configuration/memory 102 and relay task 57 checks passed. RTOS/NOR/GPIO are mocked.
- HA card: browser tests with mock HA states/services passed (Timer remaining display, click opens matching number, unavailable handling, PC/mobile layouts). Actual HA display confirmed by the user.
- Native ARM FWR decoding roundtrip passed. Full OTA regression was not repeated for the final MQTT-only change; the earlier countdown build passed 142 checks with mocked flash/HTTP/reset.
- Static memory bounds: RTOS heap 39936 bytes, reserved MSP 4096 bytes, main RAM gap 1844 bytes, CPU-only TCM cache 7552 bytes, bounded newlib remainder 17024 bytes. These are linked bounds, not measured runtime high-water values.

The user reported successful timer operation and card display on their device/HA. No automated physical boot, load, long-term network or full hardware-variant validation is claimed for this build.
