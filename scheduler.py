import time

class Task:
    def __init__(self, name, period, priority, func):
        self.name = name
        self.period = period        # 주기 (ms 단위 등)
        self.priority = priority    # 숫자가 낮을수록 높은 우선순위 (RMS 원칙)
        self.func = func            # 실행할 함수
        self.last_run = 0
        self.deadline_miss_count = 0

class RMSScheduler:
    def __init__(self):
        self.tasks = []
        self.is_safe_mode = False
        self.consecutive_misses = 0

    def add_task(self, name, period, priority, func):
        self.tasks.append(Task(name, period, priority, func))
        # 우선순위 기준 정렬 (RMS: 주기가 짧을수록 높은 우선순위)
        self.tasks.sort(key=lambda x: x.priority)

    def step(self):
        """메인 루프에서 틱(Tick)마다 호출되는 함수"""
        if self.is_safe_mode:
            return "SAFE_MODE"

        current_time = time.time() * 1000 # 밀리초 변환
        for task in self.tasks:
            if current_time - task.last_run >= task.period:
                start_t = time.time() * 1000
                success = task.func()
                end_t = time.time() * 1000
                                                                                                      # Deadline 체크 (예: 주기의 80%를 넘으면 미스로 간주)
                execution_time = end_t - start_t
                if execution_time > task.period:
                    task.deadline_miss_count += 1
                    self.consecutive_misses += 1
                else:
                    self.consecutive_misses = 0 # 정상 복구 시 리셋
                task.last_run = current_time
                
                # Watchdog 트리거 : 연속으로 데드라인을 놓치면 Safe Mode 진입
                if self.consecutive_misses >= 3:
                    self.is_safe_mode = True
                    return "TRIGGER_SAFE_MODE"

        return "RUNNING"
