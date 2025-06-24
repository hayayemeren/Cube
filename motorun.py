
# This will be on raspberry pi

import RPi.GPIO as GPIO
import time
import socket
import sys

# --- Configuration ---
HOST = '0.0.0.0'  # Listen on all available network interfaces
PORT = 65432      # Choose an unused port number (must match the port in solve.py on your desktop)

# --- Raspberry Pi GPIO Pin Assignments (BCM numbering) ---
# IMPORTANT: These are BCM GPIO numbers. Wire your drivers to these pins on your Pi's header.
# motorPins[motor_index] = [STEP_PIN_BCM, DIR_PIN_BCM]
MOTOR_PINS = [
    [2, 3],   # Motor 1: STEP on BCM 2, DIR on BCM 3
    [4, 5],   # Motor 2: STEP on BCM 4, DIR on BCM 5
    [6, 7],   # Motor 3: STEP on BCM 6, DIR on BCM 7
    [8, 9],   # Motor 4: STEP on BCM 8, DIR on BCM 9
    [10, 11], # Motor 5: STEP on BCM 10, DIR on BCM 11
    [12, 13]  # Motor 6: STEP on BCM 12, DIR on BCM 13
]

# --- Motor and Movement Parameters ---
DEGREES_PER_FULL_STEP = 1.8
MICROSTEPS_PER_FULL_STEP = 16  # Assuming 1/16 microstepping on all TMC2209s
# Base steps for 45-degree rotation (25 full steps * 16 microsteps = 400 microsteps)
STEPS_PER_BASE_TURN = int((45 / DEGREES_PER_FULL_STEP) * MICROSTEPS_PER_FULL_STEP)
BASE_STEP_DELAY_US = 500 # Microseconds (adjust this for motor speed on the Pi)

def setup_gpio():
    """Initializes GPIO pins for motor control."""
    GPIO.setmode(GPIO.BCM) # Use BCM GPIO numbering
    for motor_idx in range(len(MOTOR_PINS)):
        step_pin = MOTOR_PINS[motor_idx][0]
        dir_pin = MOTOR_PINS[motor_idx][1]
        
        GPIO.setup(step_pin, GPIO.OUT)
        GPIO.setup(dir_pin, GPIO.OUT)
        
        # Ensure pins are initially low/off
        GPIO.output(step_pin, GPIO.LOW)
        GPIO.output(dir_pin, GPIO.LOW)
    print("GPIO setup complete.")

def cleanup_gpio():
    """Cleans up GPIO pins to release resources."""
    GPIO.cleanup()
    print("GPIO cleanup complete.")

def rotate_motor(motor_index, direction_state, num_base_turns):
    """
    Rotates a specified motor by a given number of base turns in a specified direction.
    """
    if motor_index < 0 or motor_index >= len(MOTOR_PINS):
        print(f"Error: Invalid motor index {motor_index}. Skipping rotation.")
        return

    step_pin = MOTOR_PINS[motor_index][0]
    dir_pin = MOTOR_PINS[motor_index][1]
    
    GPIO.output(dir_pin, direction_state) # Set direction
    
    total_steps = int(STEPS_PER_BASE_TURN * num_base_turns)
    
    print(f"  Motor {motor_index + 1}: Executing {total_steps} microsteps (Delay: {BASE_STEP_DELAY_US}us)...")
    
    for _ in range(total_steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(BASE_STEP_DELAY_US / 1_000_000.0) # Convert us to seconds
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(BASE_STEP_DELAY_US / 1_000_000.0) # Convert us to seconds
    
    time.sleep(0.01) # Small delay for motor to settle

def main_server_loop():
    """Starts the TCP/IP server and listens for commands."""
    try:
        # Create a socket object
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Allow reuse of the address, useful for quick restarts
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
            s.bind((HOST, PORT)) # Bind to the host and port
            s.listen() # Start listening for incoming connections
            print(f"Listening for connections on {HOST}:{PORT}...")
            
            while True: # Keep server running to accept multiple connections/reconnections
                conn, addr = s.accept() # Accept a new connection
                with conn:
                    print(f"Connected by {addr}")
                    while True:
                        data = conn.recv(1024) # Receive data (up to 1024 bytes)
                        if not data:
                            print(f"Client {addr} disconnected.")
                            break # Connection closed by client
                        
                        command = data.decode('utf-8').strip() # Decode and strip whitespace
                        print(f"Received command: {command}")

                        # --- Parse and Execute Command ---
                        # Expected format: M<motor_index>_<direction_code>_<turns>
                        try:
                            parts = command.split('_')
                            if len(parts) == 3 and parts[0].startswith('M'):
                                motor_idx = int(parts[0][1:])
                                direction_str = parts[1]
                                turns = int(parts[2])

                                # Translate direction code (e.g., 'CW', 'CCW') to GPIO state
                                # This needs to match the direction_code sent from solve.py (e.g., 'CW' / 'CCW')
                                direction_state = GPIO.HIGH if direction_str == 'CW' else GPIO.LOW
                                # Adjust if your physical wiring requires different HIGH/LOW for CW/CCW

                                rotate_motor(motor_idx, direction_state, turns)
                                conn.sendall(b"DONE\n") # Send confirmation back to client
                            else:
                                conn.sendall(b"ERROR: Invalid format\n")
                                print("Invalid command format received.")

                        except Exception as e:
                            print(f"Error processing command: {e}")
                            conn.sendall(f"ERROR: {e}\n".encode('utf-8'))
                            
    except socket.error as e:
        print(f"Server socket error: {e}. Is port {PORT} in use? Check firewall.")
    except Exception as e:
        print(f"An unexpected error occurred in server: {e}")
    finally:
        print("Server shutting down.")
        cleanup_gpio()

if __name__ == "__main__":
    setup_gpio() # Initialize GPIO pins
    try:
        main_server_loop() # Start the server loop
    except KeyboardInterrupt:
        print("\nExecutor server stopped by user (Ctrl+C).")
    finally:
        cleanup_gpio() # Clean up GPIO on exit