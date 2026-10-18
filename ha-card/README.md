# MTTL-W01 2.0 Home Assistant 카드

한국어 | [English](README_EN.md)

독립 펌웨어 2.0.x용 Lovelace 카드입니다. 전체·채널별 센서와 타이머를 표시합니다. 펌웨어 버전과 카드 파일명을 매번 맞출 필요는 없습니다.

![Home Assistant 카드](HA_card.png)

## 설치

1. [mttl-w01-2.0-card.js](mttl-w01-2.0-card.js)를 Home Assistant의 `/config/www/`에 복사합니다.
2. **설정 → 대시보드 → 리소스**에서 `/local/mttl-w01-2.0-card.js`를 **JavaScript Module**로 등록합니다. 리소스 메뉴가 보이지 않으면 사용자 프로필에서 고급 모드를 활성화하십시오.
3. 브라우저를 새로고침하고 카드를 추가합니다.

```yaml
type: custom:mttl-w01-2-0-card
mac: 97c0123
mobile_two_rows: true
```

- `mac`: 기기 MAC 주소의 마지막 7자리. 구분자와 대소문자는 자동 정리됩니다.
- `name`: 선택 사항인 카드 제목. 생략하면 `MTTL XXXXXXX`로 표시합니다.
- `mobile_two_rows`: `true`이면 모바일 채널을 2열×2행으로 유지합니다. 기본값은 모바일 1열입니다.
- `channel_names`, `channel_icons`: 4개 채널의 이름·아이콘 배열. 비주얼 에디터에서도 설정할 수 있습니다.

전체 전력·누적량·전압·전류와 각 채널 전력·누적량·전류·온도를 표시합니다. 채널 헤더로 전원을 전환하고 센서 행을 누르면 해당 센서의 더보기 정보를 엽니다. 상단 센서는 모바일에서 3개·2개로 배치됩니다.

기기 웹에서 MQTT를 활성화하여 HA Discovery 엔티티를 먼저 생성해야 합니다. 기본 엔티티 ID를 사용합니다. 예: `switch.mttl_97c0123_sw1`, `sensor.mttl_97c0123_current1`. HA에서 엔티티 ID를 직접 변경하면 자동 연결되지 않습니다.

기존 카드에서 전환할 때는 리소스 URL뿐 아니라 YAML의 `type`도 위 이름으로 변경하십시오.

## 타이머 남은 시간과 설정 (2.0.15)

각 채널의 기존 센서 아래에는 `Timer` 행 하나만 표시합니다.

- 값은 `sensor.mttl_<MAC 마지막 7자리>_timer_remaining1`~`timer_remaining4`에서 읽어 `HH:MM:SS`로 표시합니다. 실행 중 약 5초마다 갱신됩니다. 펌웨어 2.0.16부터 OFF 상태에서는 설정 시간을 표시하며, 타이머를 사용하지 않으면 `00:00:00`입니다. 2.0.15에서는 유휴·종료·취소 시 `00:00:00`입니다. 카드에서 별도의 카운트다운을 만들지 않습니다. 카드 JS를 다시 교체할 필요는 없습니다.
- 해당 행을 누르면 대응하는 `number.mttl_<MAC 마지막 7자리>_timer1`~`timer4`의 HA 기본 더보기 창이 열립니다. **분 단위 0~1440**으로 설정하며 0은 타이머 해제입니다. 설정 시간은 이 창에서 확인합니다.
- 남은 시간 센서가 없거나 `unknown` / `unavailable`이면 `—`입니다. 클릭 가능 여부는 설정용 number의 사용 가능 상태를 따릅니다. 센서가 사용 불가여도 number가 정상이면 설정할 수 있습니다.
- 타이머 Discovery를 포함한 펌웨어와 기본 Entity ID가 필요합니다. 스케줄이 점유한 채널은 비영(0이 아닌) 입력을 거부하고 설정값 0을 유지합니다.

기존 JS를 교체한 뒤 리소스 URL을 `/local/mttl-w01-2.0-card.js?v=2.0.15-timer-label`으로 바꾸고 새로고침하세요. 기존 YAML `type`과 `mac`은 그대로 사용합니다. 펌웨어 파일은 수정하지 않습니다.
