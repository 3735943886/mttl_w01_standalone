# Third-party components

The application-authored Python code is MIT licensed (LICENSE). Components below retain their own terms and are not relicensed as MIT.

## OpenOCD and DLLs — downloaded, not in our ZIP

First use downloads the unmodified official archive:
https://github.com/openocd-org/openocd/releases/download/v0.12.0/openocd-v0.12.0-i686-w64-mingw32.tar.gz

SHA-256: d7168545a6d5df4772b6090d470650f3eb8c9732dbd19b1f9027824c7f4a6fa3

OpenOCD is GPL v2; upstream source: https://github.com/openocd-org/openocd/tree/v0.12.0 . Upstream DLL/library terms remain applicable and archive notices are retained. Files are placed in tools/openocd, not installed system-wide. Our ZIP does not redistribute this archive or its EXE/DLLs.

## RTL8710 flasher — GPL v2, matching sources included

Upstream: https://github.com/sandeepmistry/rtl8710-openocd
Commit: a764880fe093ea5ab16af62df046c1edae191a44

All upstream tracked sources, Makefile and license are included under third_party/rtl8710-source. The embedded flasher code array in tools/rtl8711af/rtl8710-legacy.ocd matches upstream script/rtl8710.ocd. The full locally modified script is included: target/DAP declarations are adapted for OpenOCD 0.12. Original copyright headers remain. The backend uses hla_swd, 100 kHz and a 262144-byte RAM buffer. It uses dump_image for binary reads, not the upstream Unix dd reader. See the upstream Makefile and licenses/GPL-2.0.txt.

## Python, Tcl/Tk, PyInstaller

Python and Tk license texts and PyInstaller's GPL license with bootloader exception are included under licenses. Runtime notices are retained. No Python/Node/SDK/compiler installation or persistent environment/registry changes are performed.

## OEM firmware — included stock 1.0.66

OEM 1.0.66 is proprietary third-party firmware, not MIT licensed. Our ZIP includes an unchanged copy of the previously published OEM FWR below. It is used automatically; no file selection or firmware download is required:
https://raw.githubusercontent.com/af950833/mttl_w01/main/work/firmware/1.0.66/comMTTL-W01_1.0.66.fwr

SHA-256: d780b578af69d52f3a05191a8e7d91a20e05085a912722327481cd5663682c04

No private device dump, credentials, SDK or compiler is bundled. Backups must not be publicly redistributed. Downloads occur after a user-started operation and are cached locally; downloading does not grant new copyright permissions.
