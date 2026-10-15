# MTTL-W01 Firmware Builder 1.0.0

[한국어](README.md) | English

Project-authored code uses the [MIT License](../LICENSE). [Third-party code and license scope](../LICENSING.md)

![MTTL-W01 Firmware Builder 1.0.0](../docs/builder-1.0.0.png)

A portable firmware builder for Windows x64. Download the [Builder ZIP](https://github.com/af950833/mttl_w01_standalone/releases/tag/builder-v1.0.0) and [firmware 2.0.13 Source ZIP](https://github.com/af950833/mttl_w01_standalone/releases/tag/v2.0.13).

## Usage

1. Extract the entire Builder ZIP into a short ASCII path such as `C:\Temp\MTTL-Builder`. Keep the EXE and `_internal` folder together. Administrator rights are not required.
2. Run `MTTL-Builder.exe`. Select the language with the **English / 한국어** button at the top right. After changing the language, close and restart the program for the change to take effect. Your selection is saved in `preferences.json` in the program folder. Compiler/SDK logs and Windows file dialogs use their own languages.
3. Read `License notices`, check acceptance, and select `1. Prepare / check tools`. The first preparation downloads approximately 197MiB from upstream distribution sites and requires internet access. If it fails, check the logs and retry.
4. Import `MTTL-W01-Source-2.0.13.zip` with `Import source ZIP`, or extract it and select the source directory containing `mttl-source.json`.
5. Select `2. Build firmware`. Only successful FWRs are saved under `output/<timestamp>/`. Failed or cancelled results are not published to output. Upload the generated FWR manually through the device firmware web page.
6. To customize, edit HTML, JavaScript or translations in `standalone/ui/`, or C/C++ in `standalone/firmware/`. Select the edited source directory and rebuild. A separate working copy is used, leaving your selected source unchanged. Each build receives a fresh build ID, so hashes also change.

## Features and limitations

The developer accepts no responsibility for problems or consequences arising from user modifications or self-built firmware. Questions and troubleshooting requests related to user modifications or builds are not supported. Please do not open issues for these topics.

- No persistent PATH, environment, registry or file-association changes. Dedicated PATH, Python and temporary-directory settings apply only to build child processes.
- SDK, compiler, Python and Node.js are managed inside the program's own folder. Offline builds are available after preparation.
- Closing the GUI during a task asks whether to cancel. Download cancellation may wait for a network response or timeout.
- The older GCC requires a short ASCII program path. Selected sources are copied to a separate working directory.
- No automatic OTA, ST-Link, device control or GitHub publishing is provided.
- Source can execute arbitrary commands. Building is not a security sandbox; only use trusted sources.
- Builds fail if modified code exceeds memory limits. A successful build does not guarantee safe or correct device operation.
- At least 2GB of free space is recommended. Download caches, logs and working folders accumulate and are not automatically deleted.
- The EXE is unsigned. Proxies, antivirus or security policies may block downloads or execution; the builder does not automatically change or bypass security settings.
- OTA and device operation of a user-built FWR have been verified. Modified firmware and fresh Windows PCs/VMs require separate checks.

Step-by-step logs are in `logs/`; download origins, versions and pinned hashes are in `dependencies.lock.json`. Logs contain local paths, so review them before sharing. See [Third-party notices](THIRD_PARTY_NOTICES.md).

## Builder source

Run `app.py` directly with Python 3.12 including Tk. Run engine tests with `python -m unittest test_engine.py`.

EXE packaging additionally requires PyInstaller 6.16.0. Use `--windowed --onedir --name MTTL-Builder` and `--add-data "dependencies.lock.json;."`. Retain the runtime license notices supplied in the distribution ZIP when redistributing.

SDK/compiler binaries are downloaded separately, not included in the Source ZIP. Third-party terms remain applicable; source publication does not grant a blanket license over all components.
