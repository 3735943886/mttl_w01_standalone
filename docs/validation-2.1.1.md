# 2.1.1 — Flash save visibility

The device dashboard displays the last verified physical journal-write time,
the last save-attempt result, and a cumulative failure count since boot.

- All calls to the settings journal are included (configuration, relay debounce,
  energy checkpoint/reset, OTA checkpoint), not just energy-only saves.
- A successful unchanged-payload comparison does not change the last-write time
  or write counter, since no physical write occurred. It clears the latest-attempt
  failure flag; the cumulative failure count is retained.
- No extra flash writes or heap allocations are introduced for diagnostics.
- The diagnostics are RAM-only and reset on reboot. No history since boot means
  no new record was written this boot, not that previously stored data is absent.
- A save before NTP synchronization is shown as saved/time not synchronized;
  its historical wall-clock time is not invented after synchronization.
- The existing status poll carries the diagnostics; no new polling requests.
  With SSE connected, the normal fallback poll is about 20 seconds, so this
  metadata may appear after the physical write rather than immediately.
- The J210 record format, hourly policy and 10-second relay debounce are unchanged.
  Upgrading from 2.1.0 retains the same stored settings and energy checkpoints.

Offline validation: actual ARM ELF telemetry 12 checks; journal 203; hourly 18;
energy 65; compressed-device UI 54; OTA form 31; dashboard loading suite passed.
Final SDK ELF OTA regression: 153 checks passed; portable core regression:
2123 checks passed. Build ID: `33231c0032fa013b`. FWR size: 332376 bytes.
SHA-256: `362f92df30f16fadcfd012ba20557ce58466f08706e99bca6cf6e1f67ae1ce9f`.
These use mocked hardware/network and do not establish physical device behavior.

The user subsequently confirmed normal operation after installation on a physical device. Failure-injection coverage remains mocked, not physical flash-fault testing.
