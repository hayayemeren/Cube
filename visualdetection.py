import cv2
import numpy as np
import json

class RubiksCubeDetector:
    def __init__(self, camera_index=0, config_file="hsv_config.json", output_file="detected_colors.json"):
        self.cap = cv2.VideoCapture(camera_index)
        self.frame = None
        self.hsv_ranges = self.load_hsv_config(config_file)
        self.output_file = output_file
        self.create_interface()
    
    def load_hsv_config(self, config_file):
        try:
            with open(config_file, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print("HSV config file not found. Using default values.")
            return {}
    
    def create_interface(self):
        cv2.namedWindow("Live Feed & Controls")
        cv2.createTrackbar("Canny Low", "Live Feed & Controls", 50, 255, lambda x: None)
        cv2.createTrackbar("Canny High", "Live Feed & Controls", 150, 255, lambda x: None)
        cv2.createTrackbar("Gaussian Blur", "Live Feed & Controls", 1, 20, lambda x: None)
        cv2.createTrackbar("Min Area", "Live Feed & Controls", 500, 5000, lambda x: None)
        cv2.createTrackbar("Max Area", "Live Feed & Controls", 5000, 20000, lambda x: None)
    
    def detect_cube(self, frame):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blur_value = cv2.getTrackbarPos("Gaussian Blur", "Live Feed & Controls")
        blur_value = max(1, blur_value * 2 + 1)
        blurred = cv2.GaussianBlur(gray, (blur_value, blur_value), 0)
        
        canny_low = cv2.getTrackbarPos("Canny Low", "Live Feed & Controls")
        canny_high = cv2.getTrackbarPos("Canny High", "Live Feed & Controls")
        edges = cv2.Canny(blurred, canny_low, canny_high)
        
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        min_area = cv2.getTrackbarPos("Min Area", "Live Feed & Controls")
        max_area = cv2.getTrackbarPos("Max Area", "Live Feed & Controls")
        
        mask = np.zeros_like(frame)
        detected_colors = []
        
        for contour in contours:
            approx = cv2.approxPolyDP(contour, 0.02 * cv2.arcLength(contour, True), True)
            area = cv2.contourArea(contour)
            if len(approx) == 4 and min_area < area < max_area:
                x, y, w, h = cv2.boundingRect(approx)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.drawContours(mask, [approx], -1, (255, 255, 255), -1)
                
                roi = frame[y:y+h, x:x+w]
                detected_color = self.detect_colors(roi)
                detected_colors.append({"position": (x, y), "color": detected_color})
        
        masked_frame = cv2.bitwise_and(frame, mask)
        return frame, masked_frame, detected_colors
    
    def detect_colors(self, roi):
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        avg_hsv = np.mean(hsv, axis=(0, 1))
        
        detected_color = "unknown"
        for color, (lower, upper) in self.hsv_ranges.items():
            lower_bound = np.array(lower)
            upper_bound = np.array(upper)
            if np.all(lower_bound <= avg_hsv) and np.all(avg_hsv <= upper_bound):
                detected_color = color
                break
        
        return detected_color
    
    def process_frame(self):
        ret, self.frame = self.cap.read()
        if not ret:
            return None, None, None
        
        original_frame = self.frame.copy()
        detected_frame, masked_frame, color_data = self.detect_cube(original_frame)
        return detected_frame, masked_frame, color_data
    
    def save_detected_colors(self, color_data):
        with open(self.output_file, "w") as file:
            json.dump(color_data, file, indent=4)
        print("Detected colors saved to", self.output_file)
    
    def run(self):
        while True:
            frame, modified_frame, color_data = self.process_frame()
            if frame is None:
                break
            
            combined_view = np.hstack((frame, modified_frame))
            cv2.imshow("Live Feed & Controls", combined_view)
            
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                self.save_detected_colors(color_data)
                print("Colors saved!")
            elif key == ord('q'):
                break
        
        self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    detector = RubiksCubeDetector()
    detector.run()