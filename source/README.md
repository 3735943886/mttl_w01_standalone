# MTTL-W01 2.0.12 — Firmware source

이 ZIP을 압축 해제한 뒤 **MTTL-Builder**에서 `mttl-source.json`이 있는 폴더를 선택하고 빌드하십시오. 원본 폴더를 직접 빌드하지 않고 별도 작업 복사본에서 실행하므로 소스 수정 내용은 보존됩니다.

- 화면·색상: `standalone/ui/index.html`
- 화면 동작: `standalone/ui/live.js`, `scheduler.js`
- 번역: `standalone/ui/i18n.js`
- 기기 제어: `standalone/firmware/`의 C/C++ 파일
- 빌드 시작: `build.py`; 실제 컴파일 목록: `analysis/build_minimal_network.py`

개인 플래시 덤프, 기기 Wi-Fi/MQTT 설정, 순정 FWR, SDK와 컴파일러는 포함하지 않습니다. `boot_identity.json`에는 OTA 호환성 확인에 사용하는 부트 코드 크기와 SHA-256만 있습니다. 장치 고유 데이터나 부트 코드 자체가 아닙니다.

Builder 1.0.0용 소스 스냅샷입니다. SDK와 일부 코드의 제3자 라이선스는 별도로 적용됩니다. 기존 파일의 저작권·라이선스 주석을 제거하지 마십시오. 일부 SDK 연결 코드는 upstream에서 유래했습니다. 소스 공개가 모든 코드에 대한 단일 라이선스 부여를 의미하지는 않습니다.

빌드 프로그램은 지정된 SDK·도구를 공식 배포처에서 내려받습니다. 최초 준비 시 인터넷이 필요하고, 준비 완료 후에는 오프라인 빌드가 가능합니다. 자동 업로드 기능은 없으며 FWR를 직접 기기 웹에서 올려야 합니다.

이번 소스 패키지는 개인 덤프 의존성을 없애기 위해 원본 펌웨어 디코더를 실행하는 비교 검사를 포함하지 않습니다. FWR 길이·체크섬·하드웨어 필드·라운드트립과 초기화 ARM 코드 모의 검사는 수행합니다. 빌드 성공은 실제 기기 안전성이나 정상 동작을 보증하지 않습니다. 메모리 여유가 작으므로 코드가 늘어나면 빌드 제한에 걸릴 수 있습니다.

소스는 임의 명령을 실행할 수 있으므로 출처를 신뢰하는 소스만 빌드하십시오. 사용자가 변경한 코드와 빌드 문제에 대한 개별 지원은 이 도구에 포함되지 않습니다.

## English

Extract this ZIP and select the directory containing `mttl-source.json` in MTTL-Builder. The builder compiles a working copy and does not edit your selected source. Edit HTML/CSS, JavaScript, translations or C/C++ files, then rebuild. Tools and SDK are downloaded from pinned upstream URLs with hash checks; no global PATH, environment or registry settings are changed.

This is the firmware source snapshot for Builder 1.0.0. No complete flash dump, stock firmware, device credentials or SDK/toolchain binaries are included. Third-party terms and existing copyright notices remain applicable; publication does not grant a blanket license over all components. Builds check the format and memory limits but do not guarantee safe device operation. Only build sources you trust.
