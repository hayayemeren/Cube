import cv2
import numpy as np
import json

class HSVColorCalibrator:
    def __init__(self, camera_index=0, output_file="hsv_config.json"):
        self.cap = cv2.VideoCapture(camera_index)
        self.frame = None
        self.hsv_ranges = {}
        self.output_file = output_file
        cv2.namedWindow("Calibration")
        cv2.setMouseCallback("Calibration", self.pick_color)
    
    def pick_color(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            hsv_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            pixel = hsv_frame[y, x]
            
            h_range = 15  # Range for hue
            s_range = 80  # Range for saturation
            v_range = 80  # Range for value
            
            lower = np.array([max(0, pixel[0] - h_range), max(0, pixel[1] - s_range), max(0, pixel[2] - v_range)])
            upper = np.array([min(179, pixel[0] + h_range), min(255, pixel[1] + s_range), min(255, pixel[2] + v_range)])
            
            print(f"Picked HSV: {pixel}, Range: {lower}-{upper}")
            
            color_name = input("Enter the color name (Red, Orange, Green, Blue, Yellow, White): ")
            if color_name.lower() == "red":
                if pixel[0] < 10 or pixel[0] > 170:
                    self.hsv_ranges["red_low"] = [lower.tolist(), upper.tolist()]
                else:
                    self.hsv_ranges["red_high"] = [lower.tolist(), upper.tolist()]
            else:
                self.hsv_ranges[color_name] = [lower.tolist(), upper.tolist()]
    
    def run(self):
        while True:
            ret, self.frame = self.cap.read()
            if not ret:
                break
            
            cv2.imshow("Calibration", self.frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()
        
        with open(self.output_file, "w") as f:
            json.dump(self.hsv_ranges, f, indent=4)
        print(f"HSV Ranges saved to {self.output_file}")

if __name__ == "__main__":
    calibrator = HSVColorCalibrator()
    calibrator.run()
