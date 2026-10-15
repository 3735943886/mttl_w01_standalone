# MTTL-W01 Firmware Builder 1.0.0

![MTTL-W01 Firmware Builder 1.0.0](../docs/builder-1.0.0.png)

우상단 **English / 한국어** 버튼으로 언어를 변경합니다. 선택은 프로그램 폴더의 preferences.json에 저장합니다. 컴파일러·SDK의 원문 진단 로그와 Windows 파일 선택창의 기본 버튼 언어는 별개입니다.

1. 빌드 프로그램 ZIP을 `C:\Temp\MTTL-Builder` 같은 짧은 영문 경로에 압축 해제합니다. EXE만 따로 옮기지 마십시오. 관리자 권한은 필요 없습니다.
2. `MTTL-Builder.exe`를 실행합니다.
3. `라이선스 안내`를 읽고 확인 체크 후 `1. 환경 준비 / 확인`을 누릅니다. 최초 인터넷 다운로드는 약 190MiB이며 시간이 걸릴 수 있습니다. 실패하면 로그를 확인하고 재시도할 수 있습니다.
4. 별도 소스 ZIP을 `소스 ZIP 가져오기`로 불러오거나, 압축 해제한 `mttl-source.json` 폴더를 선택합니다.
5. `2. 펌웨어 빌드`를 누릅니다. 성공한 FWR만 `output/<작업시각>/`에 저장됩니다. 실패·취소한 결과는 output에 발행하지 않습니다.
6. 필요하면 소스를 수정하고 다시 빌드합니다. `build` 폴더는 매번 별도로 만들어 선택한 소스를 직접 변경하지 않습니다.

## 특징과 제한

- 시스템 PATH·사용자/시스템 환경 변수·레지스트리·파일 연결을 변경하지 않습니다. 빌드 자식 프로세스에만 전용 PATH와 Python·임시 폴더 경로를 전달합니다.
- SDK·컴파일러·Python·Node.js는 프로그램 전용 폴더에서만 관리합니다. 초기 준비 후에는 오프라인 빌드할 수 있습니다.
- GUI 종료 중 작업이 있으면 취소 여부를 확인합니다. 다운로드 읽기 중 취소는 네트워크 응답/타임아웃까지 잠시 걸릴 수 있습니다.
- 구형 GCC로 인해 **프로그램 위치는 영문 경로**를 사용하십시오. 선택한 소스 폴더는 별도 작업 폴더로 복사합니다.
- 자동 OTA·ST-Link·기기 제어 기능은 없습니다. 만들어진 FWR는 사용자가 기기 웹에서 직접 올립니다.
- 소스 코드는 임의 명령을 실행할 수 있습니다. 빌드는 보안 샌드박스가 아니므로 신뢰하는 소스만 빌드하십시오.
- 수정한 코드가 메모리 한도를 초과하면 빌드가 실패합니다. 성공해도 실제 기기의 안전성·동작을 보증하지 않습니다.
- 다운로드 캐시와 작업 폴더가 누적될 수 있으므로 여유 공간 2GB 이상을 권장합니다. 자동 삭제하지 않습니다.
- 인터넷 프록시·백신·보안 정책에 따라 다운로드나 실행이 차단될 수 있습니다. 보안 설정을 자동으로 바꾸거나 우회하지 않습니다.
- 사용자 PC에서 빌드·OTA·기기 동작을 확인했습니다. 새 Windows PC/VM에서의 검증은 별도입니다. GitHub에 자동 게시하지 않습니다.

`logs`에 단계별 로그, `dependencies.lock.json`에 다운로드 출처와 고정 해시가 있습니다. 로그에는 로컬 경로가 포함되므로 외부에 공유하기 전에 확인하십시오.

## English

1. Extract the complete Builder ZIP into a short ASCII path such as C:\Temp\MTTL-Builder. Keep the EXE and _internal folder together. Administrator rights are not required.
2. Run MTTL-Builder.exe, read the license notices and check acceptance. Select Prepare / Check Environment. The first download is approximately 197MiB; internet access is required.
3. Import MTTL-W01-Source-2.0.12.zip, or extract it and select the directory containing mttl-source.json.
4. Select Build Firmware. Successful FWRs appear under output/<timestamp>/. Upload manually through the device firmware page.
5. To customize, edit standalone/ui (HTML, JavaScript and translations) or standalone/firmware (C/C++), then select the edited source directory and rebuild. Each build uses a separate working copy and a fresh build ID, so hashes change.

Tools are downloaded from pinned upstream URLs; no persistent PATH, environment or registry settings are changed. Logs and failed working copies remain separate. Allow at least 2GB of disk space. No device upload is performed. Only build trusted source. The EXE is unsigned; security software may warn. User-built FWR OTA and operation have been tested, but modified firmware and fresh Windows environments require their own checks.

## Builder source

Python 3.12 with Tk can run app.py directly. Run test_engine.py with unittest to check the engine. Packaging an EXE additionally requires PyInstaller 6.16.0: use --windowed --onedir --name MTTL-Builder and include dependencies.lock.json as data. The published ZIP also includes runtime license notices; retain these when redistributing. SDK/toolchain binaries are downloaded, not included in the source ZIP. Third-party terms remain applicable; source publication is not a blanket license grant.
