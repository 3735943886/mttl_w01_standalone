# 2.1.0 — append journal and local-hour persistence

Build `7fedec1dc7d5173d`; FWR 331904 bytes.

SHA-256 `9c35186a181ec97aa1bdb23dacf48cba0fcde4ea7b804b0f18835face0252e28`.

## Installation policy

No migration from 2.0.x. Old `MT02` records are ignored. If no valid `J210` journal record exists, defaults are loaded; Wi-Fi, MQTT, names, locks, protection, schedules, timers and accumulated software checkpoints must be configured again. The first valid raw counter observation establishes a zero-energy baseline, even when a metering IC retains its counter across OTA. No old software energy offset is imported. Physical latching relay contacts are NOT forced to match defaults. Logical state is initially unknown until controlled. Timer remaining duration is not persisted, as before.

2.0.18's web updater can stage this smaller image in either current slot. After reboot, join setup SoftAP and configure the device again. Do not assume the old IP remains assigned. No automatic old-version downgrade/reset compatibility is provided. Reinstalling 2.1.x while valid journal records remain restores those records; it is not a factory reset.

## Layout (end-exclusive bounds)

| Region | Start | End | Bytes |
|---|---|---|---:|
| Image 1 | 0x0B000 | 0x70000 | 413696 |
| Journal A | 0x70000 | 0x80000 | 65536 |
| Image 2 | 0x80000 | 0xE0000 | 393216 |
| Journal B | 0xE0000 | 0xF0000 | 65536 |

Boot/system data below 0x0B000 and vendor parameters/factory/calibration at or above 0xF0000 remain untouched by journal I/O. 0x7F000 is included in bank A per the chosen policy; lack of stock-runtime use has not been proven. SDK fast-connect persistence is disabled in this standalone build.

## Format and durability model

- 32 sectors, four 1024-byte records per sector, 128 physical record positions. At sector recycling, older records in the selected sector are dropped; this is not 128 guaranteed preserved historical backups.
- Header: `J210`, 32-bit modular sequence, length, CRC32. Payload is the existing compact settings/energy/relay envelope, without old 2KiB sidecars. Maximum permitted strings yield a 981-byte payload.
- Final 4-byte completion word at offset 1020 is programmed only after all staged bytes are read back. Every record program stays within a 256-byte page. The final page is programmed once for data and once for completion, not on every future append.
- Start from journal A. Append into erased slots; erase a new sector only when needed. Never erase the sector holding the latest committed record. Dirty slots left by interrupted programs are skipped to the next sector. Errors invalidate the RAM scan cache so a completed write with failed readback is rediscovered instead of duplicating sequence numbers.
- Boot scans all 128 positions for CRC-valid completed records; incomplete/corrupt/legacy records are ignored. Ambiguous duplicate/half-range sequence ordering fails closed. Payload decoding is validated before use.
- Save identical payloads without flash mutation. One 1KiB allocation for scanning/loading; saving comparison can use two concurrent 1KiB allocations, replacing the old contiguous 3KiB requirement. No secret payloads are logged.

## Save schedule

- On valid NTP time, detect crossing the local hourly boundary using the schedule timezone (including fractional-hour offsets). A delayed worker saves at the first available safe opportunity after the boundary, not precisely at wall-clock millisecond zero.
- First synchronization/timezone changes prime the hour without immediately saving. Forward clock jumps coalesce to one save; backward corrections do not repeat previously observed hours in that boot session.
- Unsynchronized fallback: one-hour monotonic interval; wrap-safe uptime subtraction.
- Failed periodic saves retain a pending request and retry no more often than once every five seconds. No unchanged writes.
- Configuration apply, delayed relay persistence (10 seconds after last completion), manual energy reset and OTA checkpoint remain. These save a full snapshot, not separate channel records.

## OTA and recovery

Explicit first-slot end added to the layout contract. Actual runtime uses first_end=0x70000 and protected_start=0xE0000. Planning and active-image identification enforce per-slot lengths; the staged adapter only erases/writes the validated plan. Build size is bounded by the smaller 384KiB slot. Boot slot starts and activation words are unchanged.

Known 1.0.66 and captured 1.0.68 images fit both slots. Stock web restoration does not intentionally erase journal data; stock runtime compatibility with arbitrary journal content remains a hardware test requirement. Do not promise a firmware-level factory reset after stock restoration.

Recovery tool 1.0.0 is NOT updated by this firmware-only work: its EE/EF tail guard can reject filled journals. Manual ST Link recovery needs a same-device image/plan clearing the journal banks while preserving boot and vendor data. Do not use a donor full dump. Firmware was subsequently published at the user’s request. Read-only device checks confirmed version/build, initial online state, sensor readiness and persistent configuration status. Relay control, reboot and flash reads were not performed during those checks.

## Validation

- Portable ARM core/integration: 2123 checks passed; 33 Discovery JSON objects validated.
- Actual final SDK ELF journal: 203 checks passed. 140 sequential records across both banks and wrap generated 35 sector erases. Partial writes, completion failures, completion readback failure/retry, corrupt CRC fallback, modular sequence wrap, erase failure, heap failure, unknown geometry, max-length payload roundtrip and protected-range preservation covered.
- Actual SDK hourly persistence: 18 checks passed, including local half-hour offsets, backward correction, forward jumps, timezone re-prime, failed-save retry, unchanged suppression and uptime wrap.
- Energy checkpoint/reset/barrier 65; HA timer configuration 102; relay state storage 10; scheduler/settings 470; timers/settings 158; timer remaining publication 134; sensor publication 311; protection 20; watchdog gate 12; relay owner 57; SSE 9; snapshot serialization 19 checks passed.
- JavaScript timer 51 and OTA form 31 checks passed; dashboard load/reconnect mock suites passed.
- Native FWR decode and BIN/FWR roundtrip passed. Static heap/known-stack checks passed: RTOS heap 39936, reserved MSP 4096, main RAM gap 3092 bytes. These are linked bounds, not measured runtime high-water values.
- Full final-ELF OTA regression: 153 checks passed. Both update directions, size-bound rejection, same-image behavior, failed activation and known stock restores with nonblank journal banks covered. Results are in `results/network-ota-test/runtime-validation.json`. NOR, HTTP calls, locks, reset, sensors and RTOS behavior are mocked; no physical boot, power-cut, load test or flash endurance claim.

The journal and partial-page programming must still be validated on the actual device. This file is a test build, not evidence of exhaustive hardware validation.

## Initial device observation

User reported successful installation. Read-only HTTP confirmed build `7fedec1dc7d5173d`, settings_persistent=true, online Wi-Fi, four valid sensor channels, zero reported save failures and no protection errors. Free heap was 9480 bytes, observed minimum 3368 bytes; stack high-water was not verified. No hourly save or reboot restoration was physically exercised.
