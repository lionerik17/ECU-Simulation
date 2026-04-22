import sys
import select
import tty
import termios
import can
import time
import struct

def is_key_pressed():
    # Checks if there's a key currently waiting in the terminal buffer
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

def simulate_engine():
    # Connect to the virtual CAN bus
    bus = can.interface.Bus(channel='vcan0', interface='socketcan')
    
    rpm = 800.0  # Start at idle RPM
    temperature = 20.0 # Start at ambient temperature
    MAX_RPM = 7000.0
    IDLE_RPM = 800.0

    print("Engine ECU Simulator Started!")
    print("Controls: Hold 'w' to accelerate, Hold 's' to brake. Press Ctrl+C to exit.")
    print("-" * 70)

    # Save the current terminal settings so we can restore them when we exit
    old_settings = termios.tcgetattr(sys.stdin)
    
    try:
        # Set terminal to "cbreak" mode (reads keys instantly without pressing Enter)
        tty.setcbreak(sys.stdin.fileno())

        while True:
            # 1. Read keyboard input
            active_key = None
            # Drain the input buffer and grab the most recent key pressed
            while is_key_pressed():
                active_key = sys.stdin.read(1).lower()

            # 2. Simulate Engine Logic
            if active_key == 'w':
                rpm += 150
                if rpm > MAX_RPM: rpm = MAX_RPM
            elif active_key == 's':
                rpm -= 300
                if rpm < IDLE_RPM: rpm = IDLE_RPM
            else:
                rpm -= 50  # Coast back to idle
                if rpm < IDLE_RPM: rpm = IDLE_RPM

            # Tiny idle fluctuation if resting
            display_rpm = rpm
            if active_key not in ['w', 's'] and rpm == IDLE_RPM:
                display_rpm = IDLE_RPM + (time.time() * 10) % 20

            # 3. Simulate Temperature
            if temperature < 90:
                if display_rpm > 3000:
                    temperature += 0.5  # Fast warmup
                elif display_rpm > IDLE_RPM:
                    temperature += 0.1  # Slow warmup
                
            # 4. Pack and Send the CAN message
            payload = struct.pack('>Hb5x', int(display_rpm), int(temperature))

            msg = can.Message(
                arbitration_id=0x100,
                data=payload,
                is_extended_id=False
            )

            bus.send(msg)
            
            # Format the display status
            status = "IDLE "
            if active_key == 'w': status = "ACCEL"
            if active_key == 's': status = "BRAKE"
            
            # Use \r to overwrite the same line in the terminal
            sys.stdout.write(f"\rStatus: {status:5} | RPM: {int(display_rpm):4} | Temp: {int(temperature):2}C | Bytes: {msg.data.hex()}")
            sys.stdout.flush()
            
            time.sleep(0.1)  # 10 Hz

    except KeyboardInterrupt:
        print("\n\nEngine shutting down...")
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        bus.shutdown()

if __name__ == "__main__":
    simulate_engine()