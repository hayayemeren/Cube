import random
import json
import socket
import time
# Removed: from tkinter import messagebox, Tk

# --- Pi Connection Details (MUST MATCH motor_executor_pico.py) ---
PI_IP_ADDRESS = '192.168.131.192' # !!! REPLACE WITH YOUR RASPBERRY PI PICO W'S IP ADDRESS !!!
PI_PORT = 65432                 # Must match the port on Pico W

# --- Kociemba Move to Motor Command Mapping (MUST BE IDENTICAL to solve.py and motor_executor_pico.py) ---
# This mapping dictates how your robot executes Kociemba moves.
KOCIEMBA_TO_MOTOR_MAP = {
    "U":   (0, 'CW',  1),  # Up face (2x 45deg turns for 90deg)
    "U'":  (0, 'CCW', 1),
    "U2":  (0, 'CW',  2),  # 4x 45deg turns for 180deg

    "R":   (1, 'CW',  1),  # Right face
    "R'":  (1, 'CCW', 1),
    "R2":  (1, 'CW',  2),

    "F":   (2, 'CW',  1),  # Front face
    "F'":  (2, 'CCW', 1),
    "F2":  (2, 'CW',  2),

    "D":   (3, 'CW',  1),  # Down face
    "D'":  (3, 'CCW', 1),
    "D2":  (3, 'CW',  2),

    "L":   (4, 'CW',  1),  # Left face
    "L'":  (4, 'CCW', 1),
    "L2":  (4, 'CW',  2),

    "B":   (5, 'CW',  1),  # Back face
    "B'":  (5, 'CCW', 1),
    "B2":  (5, 'CW',  2),
}

def generate_cube_scramble(length=15):
    """Generates a random Rubik's Cube scramble string."""
    faces = ["U", "R", "F", "D", "L", "B"]
    modifiers = ["", "'", "2"] # No modifier, prime, double turn
    
    scramble = []
    last_face = ""
    
    for _ in range(length):
        while True:
            face = random.choice(faces)
            # Avoid consecutive moves on the same face (e.g., U U')
            # And avoid moves on opposite faces consecutively (e.g., U D)
            if face != last_face and \
               not ((face == "U" and last_face == "D") or \
                    (face == "D" and last_face == "U") or \
                    (face == "R" and last_face == "L") or \
                    (face == "L" and last_face == "R") or \
                    (face == "F" and last_face == "B") or \
                    (face == "B" and last_face == "F")):
                break
        
        modifier = random.choice(modifiers)
        scramble.append(face + modifier)
        last_face = face
        
    return " ".join(scramble)

def send_command_to_pico(sock, command):
    """Sends a command to the Pico W and waits for 'DONE' confirmation."""
    try:
        sock.sendall(command.encode('utf-8'))
        response = sock.recv(1024).decode('utf-8').strip()
        return response == "DONE"
    except socket.error as e:
        print(f"Network communication error during shuffle: {e}")
        return False
    except Exception as e:
        print(f"Error during shuffle command send/receive: {e}")
        return False

def main():
    # Removed: root = Tk()
    # Removed: root.withdraw()

    # Step 1: Generate the scramble string
    scramble_string = generate_cube_scramble(length=20) # You can adjust scramble length
    scramble_moves = scramble_string.split()
    
    # Optional: Save scramble to a local file for logging/history
    with open("cube_scramble_log.json", "w") as f:
        json.dump({"scramble_string": scramble_string, "moves": scramble_moves}, f, indent=4)
    print("Cube Scramble Generated and logged to cube_scramble_log.json.")

    # Step 2: Display scramble data and confirm physical shuffle will start (now printed to console)
    print("\nStarting physical shuffle sequence on robot:")
    print(scramble_string)

    # Step 3: Establish network connection to Pico W and send shuffle commands
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            print(f"Connecting to Pico W at {PI_IP_ADDRESS}:{PI_PORT} for shuffle...")
            s.connect((PI_IP_ADDRESS, PI_PORT))
            print("Successfully connected to Pico W for shuffle.")

            print("Executing shuffle moves on robot...")
            for i, move in enumerate(scramble_moves):
                if move not in KOCIEMBA_TO_MOTOR_MAP:
                    print(f"Warning: Unknown scramble move '{move}'. Skipping.")
                    continue

                # Translate Kociemba move to motor command
                motor_idx, direction_code, turns_45_deg = KOCIEMBA_TO_MOTOR_MAP[move]
                
                # Format command for Pico W: M<motor_index>_<direction_code>_<turns_45_deg>\n
                command_to_send = f"M{motor_idx}_{direction_code}_{turns_45_deg}\n"

                print(f"[{i+1}/{len(scramble_moves)}] Sending shuffle command: {command_to_send.strip()}")
                if not send_command_to_pico(s, command_to_send):
                    print("Failed to get 'DONE' from Pico W during shuffle. Aborting shuffle.")
                    # Removed: messagebox.showerror
                    break
                time.sleep(0.1) # Small delay after receiving confirmation

            print("Robot shuffle sequence complete.")
            # Removed: messagebox.showinfo
            print("Cube has been shuffled!")

    except socket.error as e:
        # Removed: messagebox.showerror
        print(f"Network connection error: {e}\nEnsure Pico W is running motor_executor_pico.py and reachable.")
    except Exception as e:
        # Removed: messagebox.showerror
        print(f"An unexpected error occurred during shuffle: {e}")

if __name__ == "__main__":
    main()