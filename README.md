# SBC-FDIR-Simulator

소프트웨어 정의 위성 온보드 컴퓨터(SBC) 환경을 모사하여, **RMS(Rate Monotonic Scheduling) 실시간 스케줄러**와 **결정론적 FDIR(결함 탐지·격리·복구)** 메커니즘을 파이썬으로 구현한 로컬 시뮬레이터입니다.

임베디드 소프트웨어에서 가장 중요한 **'시간 엄수(Hard Real-time)'**와 **'극한 환경에서의 생존성(Fault Tolerance)'**을 별도의 하드웨어 부품 없이 소프트웨어 레벨에서 구현하고 검증하기 위해 제작했습니다.

---

## 🚀 무엇을 할 수 있는 프로젝트인가요? (Key Features)

1. **RMS 기반 실시간 스케줄러 (`scheduler.py`)**
   - 주기가 짧은 태스크(예: 자세 제어 센서 등)에 더 높은 우선순위를 부여하는 Rate Monotonic Scheduling 구현.
   - 태스크가 마감기한(Deadline)을 연속으로 초과할 경우 Watchdog 트리거를 발동하여 비상 모드 진입.
2. **통신 에러 모사 (`fault_inject.py`)**
   - 통신 패킷 구조 정의 및 CRC-16 체크섬을 통한 데이터 무결성 검증.
   - 의도적인 비트 반전(Bit-flip) 및 CRC 손상 에러 주입을 통해 수신 측의 오류 탐지 능력 테스트.
3. **결정론적 FDIR 상태 기계 (`fdir.py`)**
   - 확률적인 AI 판단 대신, 100% 예측 가능한 FSM(Finite State Machine) 기반의 자율 진단 및 복구 로직 구현.
   - `NOMINAL(정상)` ➡️ `DEGRADED(경고)` ➡️ `SAFE_MODE(안전 모드)` ➡️ `RECOVERING(복구 중)` 상태 천이 수행.
4. **실시간 터미널 대시보드 (`main.py`)**
   - `rich` 라이브러리를 활용해 터미널 상에서 태스크 상태와 FDIR 진단 결과를 실시간 시각화.

---

## 📐 시스템 구조도 (Architecture)

```text
[ main.py ] (실시간 관제 틱 루프 & 터미널 대시보드 UI)
     │
     ├──> [ scheduler.py ] (RMS 스케줄러 & Watchdog 타이머)
     │         └── 태스크 실행 및 Deadline Miss 감지
     │
     ├──> [ fault_inject.py ] (방산 통신 패킷 & CRC-16 검증)
     │         └── 우주 방사선(SEU) 모사 에러 주입
     │
     └──> [ fdir.py ] (결정론적 FDIR 상태 기계)
               └── 에러 누적 평가 및 Safe Mode / 자동 복구 제어
