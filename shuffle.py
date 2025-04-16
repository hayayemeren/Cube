import random
import json
from tkinter import messagebox

motors = [1, 2, 3, 4, 5]
times_turn = []
shuffle_data = {"Motor 1": None,
                "Motor 2": None,
                "Motor 3": None,
                "Motor 4": None,
                "Motor 5": None,}

for motor in range(len(motors)):

    times_turn.append(random.randint(1,5))
    shuffle_data[f"Motor {motor + 1}"] = times_turn[motor]
     
with open("cube_shuffle.json", "w") as f:
                json.dump(shuffle_data, f, indent=4)

messagebox.showinfo("Shuffle Data", shuffle_data)