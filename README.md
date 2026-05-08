# BLE RSSI Passive Motion & Occupancy Detection
Detects presence and motion by analyzing disturbances in Bluetooth Low Energy (BLE) signals with no dedicated sensors, cameras, or PIR sensors.

---

## Overview
Most motion detection requires dedicated hardware. This project passively listens to already existing BLE signals in the environment and detects motion for the disturbances a human body makes when moving.

---

## How it Works
### Physics
Bluetooth runs at 2.4 GHz, which the human body partially absorbs and reflects. A receiver in a room isn't just picking up the direct signal, it's picking up dozens of reflected copies bouncing off walls, furniture, and people, all arriving at slightly different times and strengths. When a person moves, those reflections shift, and that shows up as increased variance in the received signal strength (RSSI).

In practice: still room means low variance, someone moving nearby means higher variance, someone leaving the room entirely means variance jumps further and stays there. That last part makes it useful for occupancy detection, not just motion.

### Detection
For a rolling window of N samples, variance is computed as `σ² = (1/N) Σ (xᵢ - μ)²`. If that exceeds a threshold set during a quiet calibration period, motion is declared. A smoothing parameter requires several consecutive agreeing frames before a state change commits; this stops it from flickering when variance sits right on the threshold.

---

## Limitations
This is **NOT** a polished system. Sensitive environment changes, other devices moving, conditions changing mid session, or literally anything else that interrupts the signal could result in unreliable detections. It works well enough to distinguish motion from stillness, but don't expect consistency across various environments or beacon types.

---

## References
1. Adib, F. & Katabi, D. (2013). *See through walls with WiFi!* SIGCOMM.
2. Wang, W. et al. (2015). *Understanding and Modeling of WiFi Signal Based Human Activity Recognition.* MobiCom.
3. Palipana, S. et al. (2018). *FallDeFi: Ubiquitous Fall Detection using Commodity Wi-Fi Devices.* IMWUT.
4. Yousefi, S. et al. (2017). *A Survey on Behavior Recognition Using WiFi Channel State Information.* IEEE Communications Magazine.
5. Bleak BLE library: https://github.com/hbldh/bleak
