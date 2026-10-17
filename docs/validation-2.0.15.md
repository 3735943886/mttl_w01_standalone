# 2.0.15 validation

Build: `6c20881eb798b297`; firmware SHA-256: `2aade58a6a649e59982e4a1faa01dbf7f7a06a87baee299c6fa7f68b002ded46`.

- Portable ARM core/integration: 2099 checks passed. All 33 Discovery JSON objects validated.
- Current SDK ELF sensor publication: 311 checks passed; twenty topics, exact payloads, duplicate suppression, 300s heartbeat, stale-data rejection, queue rejection and uptime wrap.
- Current SDK ELF regressions: remaining-time packets 122, timers/settings 158, HA timer/configuration/memory 102 and relay task 57 checks passed. RTOS/NOR/GPIO are mocked.
- HA card: browser tests with mock HA states/services passed (Timer remaining display, click opens matching number, unavailable handling, PC/mobile layouts). Actual HA display confirmed by the user.
- Native ARM FWR decoding roundtrip passed. The updated duplicate-handling build passed full OTA regression: 143 checks with mocked flash/HTTP/reset; the duplicate HTTP path also verifies no reboot, unchanged activation signatures and released worker hold. OTA UI: 31 checks.
- Static memory bounds: RTOS heap 39936 bytes, reserved MSP 4096 bytes, main RAM gap 1636 bytes, CPU-only TCM cache 7552 bytes, bounded newlib remainder 17024 bytes. These are linked bounds, not measured runtime high-water values.

The user reported successful timer operation and card display on their device/HA. No automated physical boot, load, long-term network or full hardware-variant validation is claimed for this build.
