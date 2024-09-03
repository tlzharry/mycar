"""
從test_manage.py載入影像+偵測道路改良版+判斷障礙物是否在車道內(舊版)
"""
import cv2
import numpy as np

class StopObstacle:
    def __init__(self, stop_callback=None):
        self.stop_callback = stop_callback

    def stop_obstacle_image(self, image):
        height, width, _ = image.shape
        top_crop = int(height * 0.4)
        bottom_crop = int(height * 1)
        left_crop = int(width * 0.05)
        right_crop = int(width * 0.95)

        # 裁剪圖像
        cropped_image = image[top_crop:bottom_crop, left_crop:right_crop]

        # 檢測白線
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 0, 200])
        upper = np.array([170, 25, 255])
        binary = cv2.inRange(hsv, lower, upper)
        edged = cv2.Canny(binary, 50, 150, apertureSize=3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 30, minLineLength=30, maxLineGap=10)
        # lines = detect_white_lines(cropped_image)

        # 在裁剪圖像上繪製白線
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(cropped_image, (x1, y1), (x2, y2), (255, 0, 0), 2)

        # 定義白線之間的範圍
        if lines is not None:
            x_coords = []
            for line in lines:
                for x1, y1, x2, y2 in line:
                    x_coords.append(x1)
                    x_coords.append(x2)
            x_coords = np.array(x_coords)
            left_boundary = max(np.percentile(x_coords, 25), int(width * 0.1))
            right_boundary = min(np.percentile(x_coords, 75), int(width * 0.9))
        else:
            left_boundary = int(width * 0.1)
            right_boundary = int(width * 0.9)

        # 進一步裁剪圖像
        further_cropped_image = cropped_image[:, int(left_boundary):int(right_boundary)]

        if further_cropped_image.size == 0:
            return image

        gray = cv2.cvtColor(further_cropped_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 85, 255, cv2.THRESH_BINARY)

        # 反轉二值化圖像
        binary_inv = cv2.bitwise_not(binary)

        # 找出反轉後的輪廓
        contours, _ = cv2.findContours(binary_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        if contours:
            # 找到最大的輪廓
            largest_contour = max(contours, key=cv2.contourArea)

            # 計算最大的輪廓的面積
            largest_contour_area = cv2.contourArea(largest_contour)

            # 在終端機中打印輪廓大小和編號
            print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")

            # 繪製最大的輪廓
            cv2.drawContours(further_cropped_image, [largest_contour], -1, (0, 255, 0), 2)

            # 計算最大的輪廓的中心
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0

            # 繪製編號
            cv2.putText(further_cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            if largest_contour_area > 450:
                print("發現障礙物")
                self.stop_callback()

        # 在原圖像上顯示裁剪區域的輪廓
        cropped_image[:, int(left_boundary):int(right_boundary)] = further_cropped_image
        image[top_crop:bottom_crop, left_crop:right_crop] = cropped_image

        return image

