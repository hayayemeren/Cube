import json
import socket
import time

# --- Pi Connection Details ---
PI_IP_ADDRESS = '192.168.1.100' # !!! REPLACE WITH YOUR RASPBERRY PI'S IP ADDRESS !!!
PI_PORT = 65432                 # Choose an unused port number (must match Pi's motor_executor.py)

# --- Kociemba Move to Motor Command Mapping ---
# This mapping dictates how your robot executes Kociemba moves.
# It MUST be IDENTICAL to the mapping in your motor_executor.py on the Pi.
# (The motor_executor.py code below has been confirmed to match this mapping)
KOCIEMBA_TO_MOTOR_MAP = {
    "U":   (0, 'CW',  2),  # Up face
    "U'":  (0, 'CCW', 2),
    "U2":  (0, 'CW',  4),

    "R":   (1, 'CW',  2),  # Right face
    "R'":  (1, 'CCW', 2),
    "R2":  (1, 'CW',  4),

    "F":   (2, 'CW',  2),  # Front face
    "F'":  (2, 'CCW', 2),
    "F2":  (2, 'CW',  4),

    "D":   (3, 'CW',  2),  # Down face
    "D'":  (3, 'CCW', 2),
    "D2":  (3, 'CW',  4),

    "L":   (4, 'CW',  2),  # Left face
    "L'":  (4, 'CCW', 2),
    "L2":  (4, 'CW',  4),

    "B":   (5, 'CW',  2),  # Back face
    "B'":  (5, 'CCW', 2),
    "B2":  (5, 'CW',  4),
}


def load_solution_from_file(filename="cube_solution.json"):
    """Loads the solution string directly from the cube_solution.json file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
            # Assuming 'solution' key holds the Kociemba solution string
            return data.get("solution", "").split() # Split into list of individual moves
    except FileNotFoundError:
        print(f"Error: Solution file '{filename}' not found. Please run manual input or visual detection first to generate a solution.")
        return []
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{filename}'. File might be empty or corrupted.")
        return []
    except Exception as e:
        print(f"An unexpected error occurred loading solution from file: {e}")
        return []

def send_command_to_pi(sock, command):
    """Sends a command to the Pi and waits for 'DONE' confirmation."""
    try:
        sock.sendall(command.encode('utf-8')) # Send command as bytes
        response = sock.recv(1024).decode('utf-8').strip() # Receive response
        return response == "DONE"
    except socket.error as e:
        print(f"Network communication error: {e}")
        return False
    except Exception as e:
        print(f"Error during command send/receive: {e}")
        return False

def main():
    # Load the pre-calculated solution from the JSON file
    solution_moves = load_solution_from_file() 
    if not solution_moves:
        print("Exiting: No valid solution loaded from cube_solution.json.")
        return

    try:
        print(f"Loaded solution with {len(solution_moves)} moves. Connecting to Raspberry Pi...")

        # --- Establish network connection to Raspberry Pi ---
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((PI_IP_ADDRESS, PI_PORT)) # Connect to the Pi
            print(f"Successfully connected to Raspberry Pi at {PI_IP_ADDRESS}:{PI_PORT}")

            print("Executing moves on robot...")
            for i, move in enumerate(solution_moves):
                if move not in KOCIEMBA_TO_MOTOR_MAP:
                    print(f"Warning: Unknown Kociemba move '{move}'. Skipping.")
                    continue

                # Translate Kociemba move to motor command
                motor_idx, direction_code, turns = KOCIEMBA_TO_MOTOR_MAP[move]
                command_to_send = f"M{motor_idx}_{direction_code}_{turns}\n" # Format command for Pi

                print(f"[{i+1}/{len(solution_moves)}] Sending: {command_to_send.strip()}")
                if not send_command_to_pi(s, command_to_send):
                    print("Failed to get 'DONE' from Pi or communication error. Aborting solution.")
                    break # Stop execution if communication fails
                time.sleep(0.1) # Small delay after receiving confirmation

            print("Robot execution sequence complete.")

    except socket.error as e:
        print(f"Network connection error: {e}. Ensure Raspberry Pi is powered on, running motor_executor.py, and reachable at {PI_IP_ADDRESS}:{PI_PORT}.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()