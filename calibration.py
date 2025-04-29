import cv2
import numpy as np
import json
import os

def nothing(x):
    pass

# Color names to calibrate
colors = ["Red", "Blue", "Yellow", "Green", "Orange", "White"]
hsv_ranges = {}

cap = cv2.VideoCapture(2)
cv2.namedWindow("Calibration")

# Create trackbars
for t in ["L-H", "L-S", "L-V", "U-H", "U-S", "U-V"]:
    cv2.createTrackbar(t, "Calibration", 0 if 'L' in t else 255, 255, nothing)

# Calibration loop
for color in colors:
    print(f"Calibrating {color}... Press SPACE when ready to save this color.")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        # Get HSV values from trackbars
        l_h = cv2.getTrackbarPos("L-H", "Calibration")
        l_s = cv2.getTrackbarPos("L-S", "Calibration")
        l_v = cv2.getTrackbarPos("L-V", "Calibration")
        u_h = cv2.getTrackbarPos("U-H", "Calibration")
        u_s = cv2.getTrackbarPos("U-S", "Calibration")
        u_v = cv2.getTrackbarPos("U-V", "Calibration")

        lower = np.array([l_h, l_s, l_v])
        upper = np.array([u_h, u_s, u_v])

        mask = cv2.inRange(hsv, lower, upper)
        result = cv2.bitwise_and(frame, frame, mask=mask)

        cv2.putText(result, f"{color}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2)
        cv2.imshow("Calibration", result)

        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE to save
            hsv_ranges[color] = {
                "lower": lower.tolist(),
                "upper": upper.tolist()
            }
            break
        elif key == 27:
            break

cap.release()
cv2.destroyAllWindows()

# Save HSV ranges
with open("cube_config.json", "w") as f:
    json.dump(hsv_ranges, f, indent=4)
print("Saved to hsv_ranges.json ✅")
