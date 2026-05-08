import asyncio
import json
from detector import MotionDetector
from bleak import BleakScanner
from scanner import Sample, Buffer, BLKScanner
import argparse

async def list_devices():
    devices = {}
    
    def on_detect(device, adv):
        devices[device.address] = (device, adv)
    
    async with BleakScanner(detection_callback=on_detect) as scanner:
        await asyncio.sleep(8.0)
    
    if not devices:
        print("[!] No devices found")
        return
        
    for device, adv in sorted(devices.values(), key=lambda x: x[1].rssi, reverse=True):
        print(f"{device.address}  {adv.rssi} dBm  {device.name or '—'}")


async def run(threshold: float):
    if threshold is not None:
        print(f"[!] Input a threshold")
        return
    
    scanner = BLKScanner("target") # currently we just find the strongest device and lock onto it, later on we can add manual selection 
    detector = MotionDetector(30, threshold=threshold, smoothing=3)
    
    def on_sample(sample: Sample):
        result = detector.process_single(sample.rssi)
        print(f"{sample.addr}  {result.state.name}  var:{result.variance:.2f}")
        print(json.dumps({"timestamp": sample.timestamp, "rssi": sample.rssi, "state": result.state.name, "variance": result.variance, "mean_rssi": result.mean_rssi, "threshold": result.threshold, "window": result.window}))

    await scanner.start(ons=on_sample)


def main():
    print("[+] entered main")

    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true") 
    parser.add_argument("--threshold", type=float, required=False)
    args = parser.parse_args()
    
    if args.list:
        asyncio.run(list_devices())
    else:
        asyncio.run(run(args.threshold)) 


if __name__ == "__main__":
    main()

