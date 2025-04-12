import tkinter as tk
from tkinter import messagebox
import json

class CubeColorInput:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Cube Color Input")
        self.root.geometry("800x600")
        
        self.colors = ["white", "yellow", "red", "orange", "blue", "green"]
        self.selected_color = tk.StringVar(value=self.colors[0])
        self.squares = {face: [] for face in range(6)}
        self.face_names = ["Front", "Back", "Left", "Right", "Top", "Bottom"]
        self.middle_colors = {0: "white", 1: "yellow", 2: "red", 3: "orange", 4: "green", 5: "blue"}
        
        self.create_color_buttons()
        self.create_cube_grids()
        self.create_erase_button()
        self.create_save_button()
    
    def create_color_buttons(self):
        frame = tk.Frame(self.root)
        frame.pack(pady=10)
        
        for color in self.colors:
            btn = tk.Radiobutton(frame, text=color.capitalize(), variable=self.selected_color, value=color, indicatoron=0, width=10, bg=color)
            btn.pack(side=tk.LEFT, padx=5)
    
    def create_cube_grids(self):
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack(pady=20)
        
        for face in range(6):
            face_label = tk.Label(self.grid_frame, text=self.face_names[face], font=("Arial", 12, "bold"))
            face_label.grid(row=(face // 3) * 4, column=(face % 3) * 4 + 1, pady=5, columnspan=3)
            
            for row in range(3):
                for col in range(3):
                    bg_color = "black" if not (row == 1 and col == 1) else self.middle_colors[face]
                    btn = tk.Button(self.grid_frame, width=6, height=3, bg=bg_color)
                    btn.config(command=lambda b=btn: self.color_square(b))
                    btn.grid(row=(face // 3) * 4 + row + 1, column=(face % 3) * 4 + col, padx=5, pady=5)
                    
                    self.squares[face].append((btn, row, col))  # Store row and col info
    
    def create_erase_button(self):
        erase_btn = tk.Button(self.root, text="Erase All Colors", command=self.erase_colors, height=2, width=20)
        erase_btn.pack(pady=10)
    
    def create_save_button(self):
        save_btn = tk.Button(self.root, text="Save Colors", command=self.save_colors, height=2, width=20)
        save_btn.pack(pady=10)
    
    def color_square(self, button):
        button.config(bg=self.selected_color.get())
    
    def erase_colors(self):
        for face in range(6):
            for btn, row, col in self.squares[face]:
                if not (row == 1 and col == 1):  # Don't erase middle squares
                    btn.config(bg="black")
        messagebox.showinfo("Reset", "All colors have been erased.")
    
    def save_colors(self):
        color_data = {}
        for face in range(6):
            face_colors = []
            for btn, _, _ in self.squares[face]:
                face_colors.append(btn["bg"])
            color_data[self.face_names[face]] = face_colors
        
        with open("cube_colors.json", "w") as file:
            json.dump(color_data, file, indent=4)
        
        messagebox.showinfo("Saved", "Cube colors have been saved successfully!")

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeColorInput(root)
    root.mainloop()
