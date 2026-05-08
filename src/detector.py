import numpy as np
from collections import deque
from dataclasses import dataclass
from enum import Enum

class State(Enum): 
    UNKNOWN = 0 
    IDLE = 1
    MOVING = 2

@dataclass
class Result:
    state: State
    variance: float
    mean_rssi: float
    threshold: float
    window: int

class MotionDetector:
    def __init__(self, window_size: int = 30, threshold: float = None, smoothing: int = 3):
        self.window_size = window_size
        self.threshold = threshold
        self.smoothing = smoothing

        self._window: deque[int] = deque(maxlen=window_size)
        self._state = State.UNKNOWN
        self._pending = State.UNKNOWN
        self._streak = 0

    @property
    def state(self) -> State:
        return self._state
    
    def calibrate(self, baseline_list: list[int], multiplier: float = 2.5) -> float:
        if len(baseline_list) < self.window_size:
            raise ValueError(f"[!] Not enough data for calibration, need at least: {self.window_size} samples.")

        variances = [float(np.var(baseline_list[i:i+self.window_size])) for i in range(len(baseline_list) - self.window_size + 1)] # makes sure final window is included
        baseline_var = float(np.mean(variances))
        self.threshold = baseline_var * multiplier
        print(f"[+] Calibration complete. Baseline variance: {baseline_var:.2f}, Threshold set to: {self.threshold:.2f}")
        return self.threshold

    def evaluate(self) -> Result:
        if len(self._window) < self.window_size:
            return Result(State.UNKNOWN, 0.0, 0.0, self.threshold or 0.0, len(self._window))                                                                                           
        
        arr = np.array(self._window, dtype=float)
        variance = float(np.var(arr))
        mean_rssi = float(np.mean(arr))
        raw_state = (State.MOVING if (self.threshold is not None and variance > self.threshold) else State.IDLE) # 0.0 is technically valid so we add a none check

        # prevents flickering when variance hovers near the threshold
        if raw_state == self._pending: 
            self._streak += 1
        else:
            self._pending = raw_state
            self._streak = 1

        if self._streak >= self.smoothing:
            self._state = raw_state

        return Result(state=self._state, variance=variance, mean_rssi=mean_rssi, threshold=self.threshold or 0.0, window=self.window_size)

    def process_single(self, rssi: int) -> Result:
        self._window.append(rssi)
        return self.evaluate()
    
    def process_batch(self, rssi_list: list[int]) -> list[Result]:
        return [self.process_single(r) for r in rssi_list]