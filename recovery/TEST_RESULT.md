# Recovery 1.1 validation

- Offline unittest scenarios cover stock FWR identity/checksum, boot/map rejection, double backup mismatch, protected boot/factory preservation, both full 64KiB storage banks, legacy/J210/torn/arbitrary records, write failures and readback failures without reset.
- Windows x64 EXE and extracted portable ZIP self-tests verify GUI languages, included firmware, runtime hashes and OpenOCD version without USB access.
- Stock 1.0.66 remains the bundled recovery target. No version selection or migration is required; standalone settings/energy are erased.
- Physical ST Link V2 reads, target erase/write, reset and recovery boot have NOT been tested with this integrated tool. Offline tests are not evidence of physical recovery success. Pre-release status is retained.
- Backup-only is the default. Boot/factory/calibration areas remain protected. No device backups, credentials or sessions are distributed.
