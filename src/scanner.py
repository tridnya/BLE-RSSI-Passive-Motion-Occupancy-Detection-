import asyncio
from re import match
import time
from collections import deque
from dataclasses import dataclass, field
from bleak import BleakScanner

@dataclass
class Sample:
    timestamp: float
    rssi: int   
    addr: str

@dataclass
class Buffer:
    addr: str
    max_len: int = 200
    samples: deque = field(default_factory=lambda: deque(maxlen=200))

    def __post_init__(self): # cant be set dynamically so we init here
        self.samples = deque(maxlen=self.max_len)

    def append(self, sample: Sample):
        self.samples.append(sample)

    def as_rssi(self) -> list[int]:
        return [s.rssi for s in self.samples]


class BLKScanner:
    def __init__(self, target: str, interval: float = 0.5):
        self.target = target.lower()
        self.poll_interval = interval
        self.buffer = Buffer(addr=target)
        self._running = False


    def if_matches(self, device) -> bool:
        name = (device.name or "").lower()
        return self.target in name or self.target in device.address.lower()
        
    async def start(self, ons=None): # for testing will revert back to needing a target
        self._running = True
        self._locked_addr = None
        while self._running:
            devices = await BleakScanner.discover(timeout=self.poll_interval, return_adv=True)
            if not devices:
                continue 
            
            if self._locked_addr is None:
                device, adv = max(devices.values(), key=lambda x: x[1].rssi)
                self._locked_addr = device.address
                print(f"[+] Locked onto {self._locked_addr}")
            else:
                match = devices.get(self._locked_addr)
                if match is None:
                    await asyncio.sleep(0)
                    continue
                device, adv = match

            sample = Sample(timestamp=time.time(), rssi=adv.rssi, addr=device.address)
            self.buffer.append(sample)
            if ons:
                ons(sample)
        
            await asyncio.sleep(0)

    def stop(self):
        self._running = False
