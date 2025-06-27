from machine import Pin
import time
import network
import socket
import sys

# --- Wi-Fi Configuration ---
# IMPORTANT: Replace with your Wi-Fi credentials
SSID = 'picow'
PASSWORD = 'sbgsbg12'

# --- Server Configuration ---
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 65432      # Must match the port in solve.py on your desktop

# --- Raspberry Pi Pico W GPIO Pin Assignments ---
# Each sub-list represents a motor: [STEP_PIN_GP_NUMBER, DIR_PIN_GP_NUMBER]
# These are GPIO (GP) numbers on the Pico W.
motor_pins = [
    [0, 1],   # Motor 1: STEP on GP0, DIR on GP1
    [2, 3],   # Motor 2: STEP on GP2, DIR on GP3
    [4, 5],   # Motor 3: STEP on GP4, DIR on GP5
    [6, 7],   # Motor 4: STEP on GP6, DIR on GP7
    [8, 9],   # Motor 5: STEP on GP8, DIR on GP9
    [10, 11]  # Motor 6: STEP on GP10, DIR on GP11
]

# --- Motor and Movement Parameters ---
DEGREES_PER_FULL_STEP = 1.8
MICROSTEPS_PER_FULL_STEP = 16 
STEPS_PER_BASE_TURN = int((45 / DEGREES_PER_FULL_STEP) * MICROSTEPS_PER_FULL_STEP) 
BASE_STEP_DELAY_US = 100 # Microseconds (adjust this for motor speed on the Pico W)

# --- Kociemba Move Direction Mapping ---
# This mapping dictates the GPIO state for CW/CCW.
# You will need to test which value (1 or 0) corresponds to CW/CCW for your motors.
# This is used when parsing the 'CW'/'CCW' string from the desktop.
DIR_HIGH_IS_CW = 1 # Set to 1 if HIGH (1) on DIR pin means Clockwise, 0 if LOW (0) means Clockwise.
                   # Adjust based on physical testing.

def setup_gpio():
    """Initializes GPIO pins for motor control."""
    for motor_idx in range(len(motor_pins)):
        step_pin_num = motor_pins[motor_idx][0]
        dir_pin_num = motor_pins[motor_idx][1]
        
        # Configure pins as outputs and ensure they are low initially
        Pin(step_pin_num, Pin.OUT).value(0)
        Pin(dir_pin_num, Pin.OUT).value(0)
        
    print("GPIO setup complete.")

def rotate_motor(motor_index, direction_state, num_base_turns):
    """
    Rotates a specified motor by a given number of base turns in a specified direction.
    """
    if motor_index < 0 or motor_index >= len(motor_pins):
        print(f"Error: Invalid motor index {motor_index}. Skipping rotation.")
        return

    step_pin = Pin(motor_pins[motor_index][0], Pin.OUT)
    dir_pin = Pin(motor_pins[motor_index][1], Pin.OUT)
    
    dir_pin.value(direction_state) # Set direction
    
    total_steps = int(STEPS_PER_BASE_TURN * num_base_turns)
    
    print(f"  Motor {motor_index + 1}: Executing {total_steps} microsteps (Delay: {BASE_STEP_DELAY_US}us)...")
    
    for _ in range(total_steps):
        step_pin.value(1) # Pulse HIGH
        time.sleep_us(BASE_STEP_DELAY_US) # Microsecond delay
        step_pin.value(0) # Pulse LOW
        time.sleep_us(BASE_STEP_DELAY_US) # Microsecond delay
    
    time.sleep_ms(10) # Small delay for motor to settle

def connect_to_wifi(ssid, password):
    """Connects the Pico W to the specified Wi-Fi network."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print(f"Connecting to WiFi network: {ssid}...")
    wlan.connect(ssid, password)
    
    max_attempts = 20
    attempt_count = 0
    while not wlan.isconnected() and attempt_count < max_attempts:
        print(f"Attempt {attempt_count+1}/{max_attempts}: Waiting for connection...")
        time.sleep(1)
        attempt_count += 1

    if wlan.isconnected():
        status = wlan.ifconfig()
        print("\nSuccessfully connected to Wi-Fi!")
        print("Pico W IP Address:", status[0])
        print("Subnet Mask:", status[1])
        print("Gateway:", status[2])
        print("DNS:", status[3])
        return True
    else:
        print("\nFailed to connect to Wi-Fi.")
        print("Please check SSID, password, and Wi-Fi signal.")
        return False

def main_server_loop():
    """Starts the TCP/IP server and listens for commands."""
    try:
        # Create a socket object
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Allow address reuse
        s.bind((HOST, PORT))
        s.listen(1) # Listen for one incoming connection
        print(f"Listening for connections on {HOST}:{PORT}...")
        
        while True: # Keep server running to accept multiple connections/reconnections
            conn, addr = s.accept() # Accepts a new connection
            with conn:
                print(f"Connected by {addr}")
                while True:
                    data = conn.recv(1024) # Receive data (up to 1024 bytes)
                    if not data:
                        print(f"Client {addr} disconnected.")
                        break # Connection closed by client
                    
                    command = data.decode('utf-8').strip()
                    print(f"Received command: {command}")

                    # --- Parse and Execute Command ---
                    # Expected format from desktop solve.py: M<motor_index>_<direction_code>_<turns>
                    try:
                        parts = command.split('_')
                        if len(parts) == 3 and parts[0].startswith('M'):
                            motor_idx = int(parts[0][1:])
                            direction_str = parts[1] # e.g., 'CW' or 'CCW'
                            turns = int(parts[2])

                            # Translate direction string to GPIO state based on DIR_HIGH_IS_CW
                            if direction_str == 'CW':
                                direction_state = DIR_HIGH_IS_CW
                            elif direction_str == 'CCW':
                                direction_state = 1 - DIR_HIGH_IS_CW # Opposite of CW state
                            else:
                                raise ValueError("Invalid direction code")

                            rotate_motor(motor_idx, direction_state, turns)
                            conn.sendall(b"DONE\n") # Send confirmation back to client
                        else:
                            conn.sendall(b"ERROR: Invalid format\n")
                            print("Invalid command format received.")

                    except Exception as e:
                        print(f"Error processing command: {e}")
                        conn.sendall(f"ERROR: {e}\n".encode('utf-8'))
                            
    except OSError as e: # Catch socket-specific errors
        print(f"Server socket error: {e}. Is port {PORT} in use? Check network configuration.")
        if e.args[0] == 98: # EADDRINUSE error code
            print("Address already in use. Try restarting Pico W or choosing a different port.")
    except Exception as e:
        print(f"An unexpected error occurred in server: {e}")
    finally:
        print("Server shutting down.")
        # No explicit cleanup for MicroPython pins on script termination,
        # but a hard reset (machine.reset()) can clear pin states for next run.

# --- Main Program Entry Point ---
if __name__ == "__main__":
    setup_gpio() # Initialize GPIO pins
    
    if connect_to_wifi(SSID, PASSWORD):
        try:
            main_server_loop()
        except KeyboardInterrupt:
            print("\nExecutor server stopped by user (Ctrl+C).")
        except Exception as e:
            print(f"Main loop error: {e}")
        finally:
            # Optionally, reset the Pico W to clear all states for next run
            # import machine
            # machine.reset()
            pass
    else:
        print("Failed to connect to Wi-Fi. Cannot start server.")
