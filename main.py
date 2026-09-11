import time
import random
from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout

from scheduler import RMSScheduler
from fault_inject import DefensePacket
from fdir import FDEngine, FDIRState

# 시스템 컴포넌트 초기화
scheduler = RMSScheduler()
fdir_engine = FDEngine()

# 가상 태스크 함수 정의 (RMS 스케줄러에 등록될 작업들)
def task_attitude_control():
    # 1단계 태스크: 자세 제어 센서 모사 (짧은 주기, 높은 우선순위)
    time.sleep(0.01) # 짧은 연산 시뮬레이션
    return True

def task_telemetry_packet():
        # 2단계 태스크: 통신 패킷 생성 및 무결성 검증
    seq = random.randint(1000, 9999)
    packet = DefensePacket(seq_id=seq, payload="SAT_STATUS_OK")
                            
    # 간헐적으로 우주 방사선/전파 교란 에러 주입 (15% 확률)
    if random.random() < 0.15:
        fault_type = random.choice(["bit_flip", "crc_corruption"])
        packet.inject_fault(mode=fault_type)
                                                   
    is_valid = packet.verify_integrity()
    return is_valid

    # 스케줄러에 태스크 등록 (이름, 주기(ms), 우선순위, 함수)
scheduler.add_task("T1_AttitudeCtrl", period=100, priority=1, func=task_attitude_control)
scheduler.add_task("T2_CommsLink", period=300, priority=2, func=task_telemetry_packet)

def generate_dashboard(sim_time, packet_stat, fdir_status):
    #터미널 대시보드 레이아웃 생성
    layout = Layout()
    layout.split_column(
        Layout(name="header", size=3),
        Layout(name="body"),
        Layout(name="footer", size=3)
    )
                                                                                                
        # 헤더 패널
    layout["header"].update(
        Panel(f"[bold cyan]SBC (On-Board Computer) Real-time FDIR & RMS Simulator[/bold cyan] | Sim Time: {sim_time}s", style="bold white on blue")
    )
        
        # 바디 섹션 (좌우 분할)
    layout["body"].split_row(
        Layout(name="left"),
        Layout(name="right")
    )
                                                                                                                
        # 좌측: 스케줄러 & 태스크 상태 테이블
    task_table = Table(title="RMS Task Status", expand=True)
    task_table.add_column("Task Name", style="cyan")
    task_table.add_column("Period", justify="right")
    task_table.add_column("Priority", justify="right")
    task_table.add_column("Miss Count", justify="right", style="red")

    for t in scheduler.tasks:
        task_table.add_row(t.name, f"{t.period}ms", str(t.priority), str(t.deadline_miss_count))
    
    layout["body"]["left"].update(Panel(task_table, title="[1] Real-time Scheduler"))
                                                                                                                                                                        
        # 우측: FDIR 상태 및 통신 패킷 모니터링
    fdir_color = "green" if fdir_status == FDIRState.NOMINAL else ("yellow" if fdir_status == FDIRState.DEGRADED else "red")
    right_text = f"""
    [bold]System FDIR State:[/bold] [{fdir_color}]{fdir_status}[/{fdir_color}]
    [bold]Telemetry & Fault Stats:[/bold]
    - Packet Total Sent: {packet_stat['total']}
    - CRC/Bit Errors Detected: [red]{packet_stat['errors']}[/red]
    - Consecutive Misses: {scheduler.consecutive_misses}
    - Recovery Retries: {fdir_engine.recovery_attempts} / {fdir_engine.max_recovery_retries}
                                                                                            """
    layout["body"]["right"].update(Panel(right_text, title="[2] FDIR & Fault Monitor"))
                                                                                          # 푸터 안내 문구
    layout["footer"].update(
        Panel("[dim]Press Ctrl+C to exit simulation. Simulating Space SEU & Fault-Tolerance...[/dim]")
    )
    return layout

def main():
    sim_time = 0
    packet_stat = {"total": 0, "errors": 0}
                                                                                                # 터미널 실시간 라이브 렌더링 시작
    with Live(refresh_per_second=10) as live:
        try:
            while True:
                # 스케줄러 스텝 실행 및 상태 확인
                sched_status = scheduler.step()
                    
                # 통신 태스크 강제 1회 수행하여 패킷 에러 통계 수집
                packet_valid = task_telemetry_packet()
                packet_stat["total"] += 1
                if not packet_valid:
                    packet_stat["errors"] += 1
                        
                    # FDIR 엔진에 스케줄러 상태와 패킷 유효성 전달하여 평가
                current_fdir_state = fdir_engine.evaluate(sched_status, packet_valid)
                # 만약 FDIR이 Safe Mode 진입 후 복구를 마쳤다면 스케줄러 상태 리셋
                if current_fdir_state == FDIRState.NOMINAL and scheduler.is_safe_mode:
                    scheduler.is_safe_mode = False
                    scheduler.consecutive_misses = 0
                                                                                                          # 대시보드 갱신
                live.update(generate_dashboard(sim_time, packet_stat, current_fdir_state))
                time.sleep(0.1) # 100ms 틱 대기
                sim_time += 1
    
        except KeyboardInterrupt:
            print("\n[INFO] Simulation terminated by user.")


if __name__ == "__main__":
    main()

