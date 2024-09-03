import cv2
import numpy as np

class StopLineDetector:
    def __init__(self, stop_callback=None, resume_callback=None):
        self.stop_callback = stop_callback
        self.resume_callback = resume_callback

    # def read_file(self, file_path):
    #     try:
    #         with open(file_path, 'r') as file:
    #             content = file.read()
    #             # print("檔案內容")
    #             # print(content)
    #             return content
    #     except FileNotFoundError:
    #         print("檔案找不到")
    #         return None
    #     except IOError:
    #         print("讀取檔案時發生錯誤")
    #         return None

    def process_image(self, image):
        # 設定ROI，只關注畫面下方30%
        height = image.shape[0]
        roi_start = int(height * 0.7)
        roi = image[roi_start:, :]

        # 將影像轉換為HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 定義白色的HSV範圍
        lower_white = np.array([0, 0, 200])
        upper_white = np.array([180, 30, 255])

        # 篩選出白色區域
        mask = cv2.inRange(hsv, lower_white, upper_white)

        # 使用邊緣檢測
        edged = cv2.Canny(mask, 50, 150)

        # # 使用形態學操作去除小的噪點
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        # Detect lines using Hough transform
        lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 40, minLineLength=30, maxLineGap=10)
        # line_count = 0
        # file_path = '/tmp/rsu.txt'
        # file_content = self.read_file(file_path)
        stop_line_detector = False
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    y1 += roi_start
                    y2 += roi_start
                    angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                    cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)

                    # print("讀取到的紅綠燈: ", file_content)
                    if -3 <= angle <= 3 and (x2-x1) >= 50:  # Check if the line is horizontal and (x2-x1) >= 40
                        stop_line_detector = True
                        # print(f"Line: ({x1}, {y1}) -> ({x2}, {y2}), Angle: {angle}, Len:{x2-x1}")
                        # line_count += 1
                        # if line_count >= 2:
                            # Add your stop logic here
                            # stop_line_detector = True
                            # self.stop_callback()
        if stop_line_detector:
            # print("發現停止線")
            if self.stop_callback:
                self.stop_callback()
        else:
            # print("here")
            if self.resume_callback:
                self.resume_callback()

        return image

    # def process_image(self, image):
    #     # Convert the image to grayscale
    #     gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    #     # Apply Gaussian blur to the image
    #     blur = cv2.GaussianBlur(gray, (5, 5), 0)
    #     # Apply Canny edge detection to the image
    #     edges = cv2.Canny(blur, 50, 150)
    #     # Define a region of interest for detecting stop lines
    #     mask = np.zeros_like(edges)
    #     height, width = edges.shape
    #     region = np.array([[
    #         (0, height),
    #         (width // 2, height // 2),
    #         (width, height)
    #     ]], dtype=np.int32)
    #     cv2.fillPoly(mask, region, 255)
    #     masked_edges = cv2.bitwise_and(edges, mask)
    #     # Detect lines using Hough transform
    #     lines = cv2.HoughLinesP(masked_edges, 1, np.pi / 180, threshold=50, minLineLength=50, maxLineGap=10)
    #     if lines is not None:
    #         for line in lines:
    #             for x1, y1, x2, y2 in line:
    #                 angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
    #                 cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
    #                 if -6 <= angle <= 6:  # Check if the line is horizontal
    #                     print(f"Line: ({x1}, {y1}) -> ({x2}, {y2}), Angle: {angle}")
    #                     print("發現停止線")
    #                     # Add your stop logic here
    #     return image
