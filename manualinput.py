import tkinter as tk
from tkinter import messagebox
import json
import kociemba

class CubeColorInput:
    def __init__(self, root):
        self.root = root
        self.root.title("Manual Cube Color Input")
        self.root.geometry("1280x900")
        
        self.colors = ["white", "yellow", "red", "orange", "blue", "green"]
        self.selected_color = tk.StringVar(value=self.colors[0])
        self.squares = {face: [] for face in range(6)}
        self.face_names = ["Front", "Back", "Left", "Right", "Top", "Bottom"]
        self.middle_colors = {0: "white", 1: "yellow", 2: "red", 3: "orange", 4: "green", 5: "blue"}
        
        self.create_color_buttons()
        self.create_cube_grids()
        self.create_erase_button()
        self.create_action_buttons()
    
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
    
    def create_action_buttons(self):
        save_btn = tk.Button(self.root, text="Save Colors", command=self.save_colors, height=2, width=20)
        save_btn.pack(pady=10)

        solve_btn = tk.Button(self.root, text="Solve Cube", command=lambda: self.solve_from_json("cube_colors.json"), height=2, width=20)
        solve_btn.pack(pady=10)
    
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

    def solve_from_json(self, json_path="cube_colors.json"):
        try:
            with open(json_path, "r") as file:
                cube_data = json.load(file)

            # Map file face names to Kociemba face letters
            face_order = {
                'Top': 'U',
                'Right': 'R',
                'Front': 'F',
                'Bottom': 'D',
                'Left': 'L',
                'Back': 'B'
            }

            # Use center colors to map actual face colors
            center_colors = {}
            for face, squares in cube_data.items():
                center_color = squares[4]  # center piece is always at index 4
                center_colors[center_color] = face_order[face]

            # Build the full facelet string in URFDLB order
            facelet_string = ""
            kociemba_order = ['Top', 'Right', 'Front', 'Bottom', 'Left', 'Back']

            for face in kociemba_order:
                if face == "Top":
                    for color in cube_data[face]:
                        face_label = center_colors.get(color, 'X')
                        facelet_string += face_label
                    facelet_string = facelet_string[::-1]
                else:
                    for color in cube_data[face]:
                        face_label = center_colors.get(color, 'X')
                        facelet_string += face_label
            
            if 'X' in facelet_string or len(facelet_string) != 54:
                raise ValueError("Color mapping incomplete or cube data invalid.")

            # Solve and show result
            solution = kociemba.solve(facelet_string)
            messagebox.showinfo("Cube Solution", solution)
            return solution

        except Exception as e:
            messagebox.showerror("Error", f"Could not solve the cube:\n{e}")
            return None

if __name__ == "__main__":
    root = tk.Tk()
    app = CubeColorInput(root)
    root.mainloop()
