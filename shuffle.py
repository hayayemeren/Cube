import random
import json
from tkinter import messagebox, Tk

def generate_shuffle_data(motor_count=6, min_turns=1, max_turns=5):
    """Generate random turn values for each motor."""
    shuffle_data = {
        f"Motor {i + 1}": random.randint(min_turns, max_turns)
        for i in range(motor_count)
    }
    return shuffle_data

def save_to_json(data, filename="cube_shuffle.json"):
    """Save the shuffle data to a JSON file."""
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def format_for_messagebox(data):
    """Format the dictionary into a neat string for display."""
    return "\n".join(f"{motor}: {turns} turns" for motor, turns in data.items())

def main():
    # GUI setup for messagebox
    root = Tk()
    root.withdraw()  # Hide the main Tk window

    # Step 1: Generate shuffle data
    shuffle_data = generate_shuffle_data(motor_count=6)

    # Step 2: Save to JSON
    save_to_json(shuffle_data)

    # Step 3: Display in message box
    display_text = format_for_messagebox(shuffle_data)
    messagebox.showinfo("Cube Shuffle Generated", display_text)

if __name__ == "__main__":
    main()


