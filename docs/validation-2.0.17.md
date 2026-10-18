# 2.0.17 dashboard loading recovery

Build: `981749bcbdfe3915`

FWR: [comMTTL-W01_2.0.17.fwr](../firmware/comMTTL-W01_2.0.17.fwr)

SHA-256: `534dae7fb9dc5d23fd70a756dbd05951aed7e7c40c97243b89fd2ee1bd327238`

## Changes

- Bundle OTA UI initialization into the common live controller instead of a separate request that can fail independently.
- Inline a small common bootstrap: load translations then controller sequentially, retry network load errors after three seconds, and display a localized loading notice. Applies to all tabs. This does not retry JavaScript runtime exceptions or promise a bounded browser transport timeout.
- Firmware status uses an eight-second request timeout, three-second retry after failures, and refresh on Firmware-tab selection or document visibility restoration. Concurrent status requests are suppressed.
- Never automatically resubmit firmware uploads. Completed/restored/uncertain upload outcomes keep the existing safety behavior and are not overwritten by background refreshes.
- Preserve existing no-store headers. No persistent polling of firmware status after a successful initial query.
- Align UI, Discovery and web API version strings to 2.0.17.
- Successful standalone OTA waits five seconds, then checks status every three seconds with five-second request timeouts for up to two minutes. Reload into the Firmware tab only after a different valid Build ID is observed. On timeout, show manual reconnect instructions without repeating the upload. Same-image and stock-restore results do not enter this loop.
- The new reconnect behavior applies to uploads initiated from the updated UI. The first installation from an older UI still requires one manual refresh.

## Validation

- JavaScript OTA form regression: 31 checks passed with mocked DOM/network.
- Added mock tests for sequential loading, failed script retries, failed status recovery, Firmware-tab/visibility refresh, single-flight request handling and timeout scheduling.
- Generated gzip assets decoded successfully: three assets; inline loader present, separate OTA request absent, all generated JavaScript passed Node syntax checks.
- ARM core/integration: 2119 checks, zero failures, 33 Discovery JSON objects validated.
- Final SDK ELF: timer publication 134, sensor publication 311, relay task 57 checks passed; heap/known C stack frame bounds passed. Hardware, RTOS and NOR are mocked.
- Native FWR decode and BIN/FWR roundtrip passed during build.
- Pre-reconnect 2.0.17 SDK ELF OTA regression: 143 checks passed, zero failures; mocked flash, HTTP calls, locks and reset. Not repeated for the final JS-only reconnect addition; no OTA writer changes.
- Reconnect mock tests cover old-build responses, reboot network failures, new-build reload, timeout, same-image behavior, stock restore, and no repeated POST. Final ELF memory bounds and timer/sensor publication tests passed.
- Static linked RAM gap 1300 bytes; reserved MSP 4096 bytes; RTOS heap 39936 bytes. Gzip assets total 19077 bytes. Not measured runtime memory high-water values.

The original browser request failure was not captured, so its exact transport/cache cause is not established. No physical device upload or GitHub publication was performed. After installation, verify normal refresh, tab reopening and language switching on the actual device.
