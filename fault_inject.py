import random
import zlib

class DefensePacket:
    def __init__(self, seq_id:int, payload:str):
        self.seq_id = seq_id
        self.payload = payload
        self.crc = self._calculate_crc()
        self.is_corrupted = False

    def _calculate_crc(self) -> int:
        #CRC-16 체크섬 계산
        data_bytes = f"{self.seq_id}:{self.payload}".encode('utf-8')
        return zlib.crc32(data_bytes) & 0xFFFF

    def inject_fault(self, mode: str = "bit_flip"):
        if mode == "bit_flip":
            if len(self.payload)>0:
                p_list = list(self.payload)
                idx = random.randint(0, len(p_list)-1)
                p_list[idx] = chr(ord(p_list[idx]) ^ 0xFF)
                self.payload = "".join(p_list)
                self.is_corrupted = True

        elif mode == "crc_corruption":
            #패킷 데이터는 멀쩡, CRC 체크섬 값 변조(전송 중 노이즈)
            self.crc ^= 0xFFFF
            self.is_corrupted = True

    def verify_integrity(self)->bool:
        #수신 측에서 CRC 재계산해 패킷 무결성 검증
        data_bytes = f"{self.seq_id}:{self.payload}".encode('utf-8')
        expected_crc = zlib.crc32(data_bytes) & 0xFFFF
        return self.crc == expected_crc
