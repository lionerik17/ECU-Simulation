import pytest
import subprocess
import time
import can
import struct

# This fixture runs automatically before the tests start.
# It launches the simulator, lets the tests run, and then kills the simulator.
@pytest.fixture(scope="module")
def ecu_process():
    print("\n[Setup] Starting ECU Simulator in the background...")
    # Launch the simulator as a separate background process
    proc = subprocess.Popen(["python3", "ecu_sender.py"])
    
    # Give the CAN bus a half-second to initialize and start broadcasting
    time.sleep(0.5) 
    
    # Let the tests run
    yield proc
    
    print("\nShutting down ECU Simulator...")
    proc.terminate()
    proc.wait()

# --- TESTS ---

def test_ecu_broadcasts_correct_id_and_length(ecu_process):
    """Verify the ECU is sending standard frames on ID 0x100 with an 8-byte payload."""
    
    with can.interface.Bus(channel='vcan0', interface='socketcan') as bus:
        # Wait up to 2 seconds for a message
        msg = bus.recv(timeout=2.0)
        
        assert msg is not None, "Failed to receive any CAN messages on vcan0."
        assert msg.arbitration_id == 0x100, f"Expected ID 0x100, got {hex(msg.arbitration_id)}"
        assert msg.is_extended_id == False, "Expected Standard ID, got Extended ID"
        assert msg.dlc == 8, f"Expected 8 bytes of data (DLC), got {msg.dlc}"

def test_ecu_initial_idle_values(ecu_process):
    """Verify that upon startup, the ECU rests at ~800 RPM and 20C."""
    
    with can.interface.Bus(channel='vcan0', interface='socketcan') as bus:
        # Sniff the bus for a message
        msg = bus.recv(timeout=2.0)
        assert msg is not None
        
        # Unpack the payload using our established CAN matrix
        rpm, temp = struct.unpack('>Hb', msg.data[0:3])
        
        # Because we added a slight idle fluctuation (800 + random),
        # we test if the RPM is within the expected idle range
        assert 800 <= rpm <= 820, f"Expected idle RPM around 800, got {rpm}"
        
        # Temperature should start exactly at 20C
        assert temp == 20, f"Expected starting temperature of 20C, got {temp}C"

def test_ecu_padding_bytes_are_zero(ecu_process):
    """Verify that the unused bytes (3 through 7) are safely zeroed out."""
    
    with can.interface.Bus(channel='vcan0', interface='socketcan') as bus:
        msg = bus.recv(timeout=2.0)
        assert msg is not None
        
        # Extract the last 5 bytes
        padding_bytes = msg.data[3:8]
        
        # They should all equal 0x00
        assert padding_bytes == bytearray([0x00, 0x00, 0x00, 0x00, 0x00]), "Padding bytes contain garbage data!"