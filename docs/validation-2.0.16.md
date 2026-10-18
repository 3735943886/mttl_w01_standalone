# 2.0.16 validation

Build: `b7ebaf1e5faa6a1a`. Firmware SHA-256: `700820e59ec73bd9a3c8d23e67180e06aad9fff54346cb0a7c3f835462f9a7f1`.

- Portable ARM core/integration: 2119 checks passed; 33 Discovery JSON objects validated.
- Current SDK ELF: retained timer publication 134, sensor publication 311, timers/settings 158, relay task 57 checks passed; OTA memory validation passed.
- Idle duration, five-second active countdown, expiry-before-OFF zero, configured value after OFF, idle setting changes, removal and reconnect synchronization covered with mocked hardware/RTOS.
- Native ARM FWR decoding and BIN/FWR roundtrip passed.
- Full OTA runtime regression was not repeated for this MQTT-only change.
- Static linked bounds: RTOS heap 39936 bytes, reserved MSP 4096 bytes, main RAM gap 1556 bytes; TCM cache 7560 bytes. These are not measured runtime high-water values.
- The user confirmed the timer behavior on the preceding 2.0.16 test build. This release rebuild additionally updates the static Firmware-page fallback version label; no device upload was performed by this release process.

OFF/idle payload is configured seconds retained once per change, not a once-per-second stream. ON countdown cadence remains five seconds. The HA card JS is unchanged.
