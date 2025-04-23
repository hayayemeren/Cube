import tkinter as tk
import subprocess


def run_calibration():
    subprocess.run(["python3", "calibration.py"])

def run_visual_detection():
    subprocess.run(["python3", "visualdetection.py"])

def run_manual_input():
    subprocess.run(["python3", "manualinput.py"])

def run_shuffle():
    subprocess.run(["python3", "shuffle.py"])
# Create the main window
root = tk.Tk()
root.title("Rubik's Cube Tools")
root.geometry("200x300")

# Create buttons
btn_calibration = tk.Button(root, text="Run Calibration", command=run_calibration, height=2, width=20)
btn_calibration.pack(pady=10)

btn_visual_detection = tk.Button(root, text="Run Visual Detection", command=run_visual_detection, height=2, width=20)
btn_visual_detection.pack(pady=10)

btn_manual_input = tk.Button(root, text="Run Manual Input", command=run_manual_input, height=2, width=20)
btn_manual_input.pack(pady=10)

btn_manual_input = tk.Button(root, text="Run  Shuffle", command=run_shuffle, height=2, width=20)
btn_manual_input.pack(pady=10)

# Run the GUI loop
root.mainloop()
