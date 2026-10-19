# 2.0.18 validation

Build: `8af7825ca26a7548`. SHA-256: `e69a14a10a4bb1348378ef7ef20e76ce5143a286d57462c7b4bb4a4fbc618ea5`.

- Native FWR decoding and BIN/FWR roundtrip passed during build.
- Generated gzip HTML checked for centered timer-card titles and 600px log height.
- Timer/settings JavaScript: 51 checks passed. OTA reconnect mock scenarios passed.
- Heap/known C stack frame bounds passed. Main RAM gap 1284 bytes; reserved MSP 4096 bytes; RTOS heap 39936 bytes. Not measured runtime high-water values.
- User confirmed normal operation on their device. Full OTA regression was not repeated for this CSS-only change.
