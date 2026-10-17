# 1.0.0 local validation

- Offline core/workflow: 13 unittest scenarios passed. Includes exact stock FWR validation, corrupt/BIN/full-dump refusal, supported map/boot identity, settings-tail guard, identical complete backups, full reconstructed image, original boot/factory preservation, partial write/readback failures, no reset on failure, archive traversal/link rejection and cached-download verification.
- Windows x64 frozen EXE self-test: Korean/English widgets initialized, stock FWR decoded, OpenOCD version query successful; no USB/target access.
- Extracted ZIP into a path containing spaces and Korean characters; frozen EXE self-test passed there. This does not validate physical target transfers in those paths.
- OpenOCD HLA SWD / RTL8710 configuration parsed, followed by shutdown before target initialization. No adapter access or writes.
- Actual ST Link V2 connection, double read, erase/write, reset and stock boot have NOT been tested with this integrated tool. The public release is explicitly marked as physically unvalidated; no physical recovery success is claimed.
- Diagnostic/backup-only mode is the default. Recovery requires explicit isolation confirmation and restore selection. Both modes keep the CPU halted on unsuccessful completion; a power-cycle is needed after successful diagnosis to boot normally.
- ZIP includes no device dump, sessions, credentials, SDK or compiler. OpenOCD EXE/DLLs and OEM FWR are not bundled; first-use pinned downloads retrieve them directly from the documented sources. GPL flasher sources and licenses are provided as described in THIRD_PARTY_NOTICES.md.
- Runtime manifest verifies the EXE, bundled Python/Tk runtime, OpenOCD executable/DLLs/scripts and stock FWR before target connection. Unit tests cover intact, modified and unsafe manifest cases. Failure logs include the last verified write step.
