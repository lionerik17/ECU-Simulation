# ECU Simulator

A simple Python-based Engine ECU simulator using the Controller Area Network (CAN) protocol. This project simulates an Engine ECU broadcasting real-time telemetry data (RPM and Temperature) over a virtual CAN bus (`vcan0`) and includes a dashboard listener to visualize the data.

## Project Structure

- `ecu_sender.py`: The Engine ECU simulator. It captures keyboard input to simulate acceleration ('w') and braking ('s') and broadcasts CAN frames.
- `ecu_listener.py`: A dashboard application that listens for CAN frames from the Engine ECU and displays the RPM and Temperature.
- `ecu_test.py`: Automated tests using `pytest` to verify the CAN frame structure and ECU logic.
- `init_vcan.sh`: A shell script to initialize the virtual CAN interface (`vcan0`) on Linux.

## CAN Frame Specification

The Engine ECU broadcasts messages with the following format:

- **Arbitration ID**: `0x100` (Standard 11-bit ID)
- **Data Length Code (DLC)**: 8 bytes
- **Payload Layout**:

| Byte(s) | Parameter | Data Type | Details |
|---------|-----------|-----------|---------|
| 0-1     | RPM       | uint16    | Big-endian unsigned short |
| 2       | Temp      | int8      | Signed char (Celsius) |
| 3-7     | Padding   | -         | Reserved (always `0x00`) |

## Simulation Logic

The ECU simulation runs at a frequency of 10Hz (0.1s intervals).

### RPM Behavior
- **Idle**: The engine starts at a baseline of 800 RPM. When idling without input, the RPM fluctuates slightly for realism.
- **Acceleration ('w')**: RPM increases by 150 per cycle, up to a maximum of 7,000 RPM.
- **Braking ('s')**: RPM decreases rapidly by 300 per cycle, down to the idle floor of 800 RPM.
- **Coasting**: If no keys are held, the RPM naturally coasts down by 50 per cycle until it hits idle.

### Temperature Behavior
The engine starts at an ambient temperature of 20°C and warms up to a maximum operating temperature of 90°C based on load:
- **Fast Warmup**: If RPM is above 3,000, temperature increases by 0.5°C per cycle.
- **Standard Warmup**: If RPM is above idle, temperature increases by 0.1°C per cycle.

## Prerequisites

- **Operating System**: Linux (required for `socketcan` and `vcan` support).
- **Python**: 3.6+
- **Kernel Modules**: `vcan` module must be available.

## Setup and Usage

### 1. Install Dependencies
Install the required Python packages:
```bash
pip install -r requirements.txt
```

### 2. Initialize Virtual CAN Interface
Run the provided script to set up `vcan0`. This requires `sudo` privileges:
```bash
chmod +x init_vcan.sh
sudo ./init_vcan.sh
```

### 3. Run the ECU Simulator
Start the Engine ECU. It will listen for keyboard inputs:
- **'w'**: Accelerate (Increase RPM)
- **'s'**: Brake (Decrease RPM)
- **Ctrl+C**: Exit

```bash
python3 ecu_sender.py
```

### 4. Run the Dashboard
In a separate terminal, start the dashboard to view the simulated engine data:
```bash
python3 ecu_listener.py
```

### 5. Running Tests
To run the automated test suite:
```bash
pytest ecu_test.py
```
