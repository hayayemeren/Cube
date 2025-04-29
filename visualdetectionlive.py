import cv2
import numpy as np
import json
import kociemba

def preprocess_frame(frame, scale_percent=100):
    width = int(frame.shape[1] * scale_percent / 100)
    height = int(frame.shape[0] * scale_percent / 100)
    dim = (width, height)
    resized = cv2.resize(frame, dim, interpolation=cv2.INTER_AREA)
    hsv = cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    return resized, hsv

def get_color_masks(hsv_frame):
    with open("cube_config.json", "r") as f:
        color_ranges = json.load(f)

    masks = {}
    kernel = np.ones((5, 5), np.uint8)

    for color, ranges in color_ranges.items():
        lower = np.array(ranges["lower"], dtype=np.uint8)
        upper = np.array(ranges["upper"], dtype=np.uint8)

        mask = cv2.inRange(hsv_frame, lower, upper)
        mask = cv2.dilate(mask, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        masks[color] = mask

    return masks

def detect_and_label_colors(frame, masks):
    detected = []
    colors_bgr = {
        "Red": (0, 0, 255),
        "Blue": (255, 0, 0),
        "Yellow": (0, 255, 255),
        "Green": (0, 255, 0),
        "Orange": (0, 128, 255),
        "White": (255, 255, 255)
    }

    for color_name, mask in masks.items():
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > 2000:
                x, y, w, h = cv2.boundingRect(contour)
                detected.append((x, y, color_name))
                cv2.rectangle(frame, (x, y), (x + w, y + h), colors_bgr[color_name], 2)
                cv2.putText(frame, color_name.lower(), (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, colors_bgr[color_name], 2)

    return frame, detected

def sort_detected(detected):
    # Sort top-to-bottom first
    detected = sorted(detected, key=lambda item: item[1])

    rows = []
    current_row = []
    last_y = None
    threshold = 50  # Tolerance for same-row grouping

    for item in detected:
        x, y, color_name = item
        if last_y is None:
            last_y = y

        if abs(y - last_y) > threshold:
            rows.append(sorted(current_row, key=lambda item: item[0]))
            current_row = []
            last_y = y

        current_row.append(item)

    if current_row:
        rows.append(sorted(current_row, key=lambda item: item[0]))

    sorted_colors = [color_name for row in rows for (_, _, color_name) in row]
    return sorted_colors

def solve_from_json(json_path="cube_detected.json"):
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
            for color in cube_data[face]:
                face_label = center_colors.get(color, 'X')
                facelet_string += face_label

        if 'X' in facelet_string or len(facelet_string) != 54:
            raise ValueError("Color mapping incomplete or cube data invalid.")

        # Solve and show result
        solution = kociemba.solve(facelet_string)
        solution_data = {
            "facelet_string": facelet_string,
            "solution": solution
        }
        with open("cube_solution.json", "w") as f:
            json.dump(solution_data, f, indent=4)

        return solution

    except Exception as e:
        print("Error:", f"Could not solve the cube:\n{e}")
        return None

def main():
    cap = cv2.VideoCapture(2)
    faces_data = {}
    face_order = ["Front", "Back", "Left", "Right", "Top", "Bottom"]
    face_index = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        resized, hsv = preprocess_frame(frame)
        masks = get_color_masks(hsv)
        result_frame, detected = detect_and_label_colors(resized, masks)

        # Show which face you are scanning
        if face_index < len(face_order):
            text = f"Scanning: {face_order[face_index]} (Press SPACE)"
        else:
            text = "All faces scanned. Press ESC."
        
        cv2.putText(result_frame, text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)

        cv2.imshow("Original Frame", resized)
        cv2.imshow("Color Detection", result_frame)

        key = cv2.waitKey(30) & 0xFF

        if key == 27:  # ESC key
            break
        elif key == 32:  # SPACE key
            if len(detected) != 9:
                print(f"⚠️ Only {len(detected)} colors detected! Make sure 9 colors are visible.")
                continue

            detected = [(x, y, color.lower()) for (x, y, color) in detected]
            sorted_colors = sort_detected(detected)[:9]
            if face_index < len(face_order):
                face_name = face_order[face_index]
                faces_data[face_name] = sorted_colors
                print(f"✅ Saved Face '{face_name}': {sorted_colors}")
                face_index += 1

                if face_index == len(face_order):  # After capturing all faces
                    # Save faces
                    with open("cube_detected.json", "w") as f:
                        json.dump(faces_data, f, indent=4)
                    print("🎯 All faces saved to cube_detected.json!")

                    # Solve cube
                    solution = solve_from_json()
                    print("🧩 Solution:", solution)

            else:
                print("✅ All 6 faces already recorded.")

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
