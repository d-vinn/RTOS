class FDIRState:
    NOMINAL = "NOMINAL(정상)"
    DEGRADED = "DEGRADED(성능 저하/경고)"
    SAFE_MODE = "SAFE_MODE(안전 모드/비상)"
    RECOVERING = "RECOVERING(복구 중)"

class FDEngine:
    def __init__(self):
        self.current_state = FDIRState.NOMINAL
        self.packet_error_count = 0
        self.consecutive_deadline_misses = 0
        self.recovery_attempts = 0
        self.max_recovery_retries = 3

    def evaluate(self, scheduler_status:str, packet_valid:bool)->str:
        #error count
        if not packet_valid:
            self.packet_error_count += 1

        if scheduler_status == "TRIGGER_SAFE_MODE":
            self.consecutive_deadline_misses += 3
        elif scheduler_status == "RUNNING":
            if self.consecutive_deadline_misses > 0:
                self.consecutive_deadline_misses -= 1

        if self.current_state == FDIRState.NOMINAL:
            if self.consecutive_deadline_misses >= 1 or self.packet_error_count >= 3:
                self.current_state = FDIRState.DEGRADED

        elif self.current_state == FDIRState.DEGRADED:
            if self.consecutive_deadline_misses >= 3 or self.packet_error_count >= 6:
                self.current_state = FDIRState.SAFE_MODE
            elif self.consecutive_deadline_misses == 0 and self.packet_error_count == 0:
                self.current_state = FDIRState.NOMINAL

        elif self.current_state == FDIRState.SAFE_MODE:
            if self.recovery_attempts < self.max_recovery_retries:
                self.current_state = FDIRState.RECOVERING

        elif self.current_state == FDIRState.RECOVERING:
            self.recovery_attempts += 1
            self.packet_error_count = 0
            self.consecutive_deadline_misses = 0
            self.current_state = FDIRState.NOMINAL

        return self.current_state

    def force_reset(self):
        self.current_state = FDIRState.NOMINAL
        self.packet_error_count = 0
        self.consecutive_deadline_misses = 0
        self.recovery_attempts = 0
