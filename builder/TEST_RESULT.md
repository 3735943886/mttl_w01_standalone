# Local test results — 2026-10-15

## 1.0.0 — 2026-10-16

The user confirmed successful builder operation, OTA installation of the generated FWR and normal operation on their device. This confirms that device/workflow, not every hardware variant or modification. Version 1.0.0 retains the tested build engine and adds release documentation.

0.1.1 adds Korean/English UI switching and folder-local language preferences. Translation and engine unit tests: 12 passed. Compiler/SDK raw diagnostics remain unchanged. GUI visual layout verification remains incomplete as described below.

- Official upstream download, pinned SHA-256 verification and local extraction: passed.
- Embedded Python 3.12.10, Node 22.14.0, GCC 4.8.3, SDK and package probes: passed.
- Source without complete flash dumps or manufacturer firmware: FWR generation passed.
- Packaged EXE CLI: environment check plus full build passed (exit 0).
- Engine unit tests: 11 passed, including archive traversal/link rejection, bad download hash, cancellation, exclusive locking, environment isolation and failed-build output suppression.
- GUI process/window starts. Visual capture returned black and activation was denied; GUI visual layout and mouse interactions are **not fully verified**. Please test the visible interface yourself.
- No firmware uploaded and no GitHub changes made.

The newly downloaded Windows compiler differs from the historical mixed local toolchain. Its FWR is 327756 bytes (historical 2.0.12 release: 327740). Both compile/link and packaging checks pass; do not describe this as a byte-identical or target-tested firmware. Actual uploaded device behavior is not yet verified for the builder-generated file.

The firmware source ZIP omits the original-decoder fixture check to avoid distributing the original firmware; format, checksum, hardware field, BIN/FWR roundtrip and setup ARM mock checks remain. Existing SDK enum ABI warnings are retained in the log and have not been resolved by this builder project.

This package is for local testing, not a finalized public redistribution release. Third-party licensing and fresh-PC validation remain separate work. Tools download on first prepare; no toolchain/SDK archive is embedded in the builder ZIP. Build and download caches accumulate only in the builder home. The EXE is unsigned.

## 한국어

실제 EXE의 명령행 경로로 환경 확인과 FWR 빌드가 성공했습니다. GUI 창은 생성되지만 화면 자동 캡처가 검게 나오고 활성화 권한이 거부되어 마우스 조작·레이아웃 확인은 완료하지 못했습니다. 사용자가 화면을 직접 확인해 주세요.

생성한 펌웨어는 공식 다운로드 컴파일러를 사용하므로 기존 배포본과 바이트가 완전히 같지는 않습니다. 형식 검사와 빌드는 통과했지만 이 결과물을 기기에 올려 검증하지는 않았습니다. 기존 동작 펌웨어를 대체하기 전에 복구 방법을 확보하고 테스트하십시오. GitHub 업로드는 하지 않았습니다.
