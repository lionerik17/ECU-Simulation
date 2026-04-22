import sys
import can
import struct

def run_dashboard():
    bus = can.interface.Bus(channel='vcan0', interface='socketcan')
    print("Dashboard listening for Engine ECU (ID: 0x100)...")
    print("-" * 60)

    try:
        while True:
            message = bus.recv(timeout=1.0)
            
            # Only process messages from Engine ECU (ID 0x100)
            if message is not None and message.arbitration_id == 0x100:
                
                # Unpack the first 3 bytes
                # '>H' for the 2-byte RPM, 'b' for the 1-byte Temp
                rpm, temp = struct.unpack('>Hb', message.data[0:3])
                
                # Use \r to overwrite the same line in the terminal
                sys.stdout.write(f"\rRPM: {rpm:4} | Temp: {temp:2}C")
                sys.stdout.flush()

    except KeyboardInterrupt:
        print("\n\nDashboard shutting down...")
    finally:
        bus.shutdown()

if __name__ == "__main__":
    run_dashboard()