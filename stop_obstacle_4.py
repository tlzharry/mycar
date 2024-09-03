"""
從test_manage.py載入影像+偵測道路改良版+判斷障礙物是否在車道內(新版)
"""
import cv2
import numpy as np

class StopObstacle:
    def __init__(self, stop_callback=None, resume_callback=None):
        self.stop_callback = stop_callback
        self.resume_callback = resume_callback

    def point_in_polygon(self, x, y, polygon):
        """
        使用射線法判斷是否在多邊形內
        :param x: 點的x座標
        :param y: 點的y座標
        :param polygon: 多邊形頂點座標列表 [(x1, y1), (x2, y2), ...]
        :return: 如果點在多邊形內,回傳True,否則回傳False
        """
        num = len(polygon)
        j = num - 1
        odd_nodes = False
        for i in range(num):
            xi, yi = polygon[i]
            xj, yj = polygon[j]
            if yi < y <= yj or yj < y <= yi:
                if x <= (xj - xi) * (y - yi) / (yj - yi) + xi:
                    odd_nodes = not odd_nodes
            j = i

        return odd_nodes

    def write_file(self, file_path, text):
        file = open(file_path, 'w')
        file.write(text)
        file.close()

    def stop_obstacle_image(self, image):
        file_path = '/tmp/car1.txt'
        run = '1'
        obstacle = '3'

        height, width = image.shape[:2]

        # 裁剪圖像
        cropped_image = image[int(height * 0.35):, int(width * 0.1):]
        new_cropped_image = cropped_image.copy()

        # 檢測白線
        hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
        lower = np.array([0, 0, 200])
        upper = np.array([180, 30, 255])
        binary = cv2.inRange(hsv, lower, upper)
        edged = cv2.Canny(binary, 50, 150, apertureSize=3)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
        lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 30, minLineLength=20, maxLineGap=10)

        # 初始化變數
        min_x = min_y = 0
        max_x = 160
        max_y = 120

        # 在裁剪圖像上繪製白線
        if lines is not None:
            for line in lines:
                for x1, y1, x2, y2 in line:
                    cv2.line(cropped_image, (x1, y1), (x2, y2), (190, 190, 190), 2)
        

            # 找出所有紅線的x和y座標
            x_coords = []
            y_coords = []
            for line in lines:
                for x1, y1, x2, y2 in line:
                    x_coords.extend([x1, x2])
                    y_coords.extend([y1, y2])
            
            # 計算紅線圍成的矩形的邊界
            min_x = min(x_coords)
            max_x = max(x_coords)
            min_y = min(y_coords)
            max_y = max(y_coords)

            # 定義車道範圍多邊形
            lane_polygon = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
            
            # 裁切影像
            new_cropped_image = cropped_image[min_y:max_y, min_x:max_x]

            if new_cropped_image.size == 0:
                return image

            # 計算矩形的中心點
            lane_cX = (min_x + max_x) // 2
            lane_cY = (min_y + max_y) // 2

            # # 在影像上繪製中心點
            # cv2.circle(new_cropped_image, (lane_cX, lane_cY), 5, (0, 255, 255), 2)  # 繪製黃色圓點

            # 判斷障礙物
            gray = cv2.cvtColor(new_cropped_image, cv2.COLOR_BGR2GRAY)
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
                # print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")
                
                # 繪製最大的輪廓
                cv2.drawContours(new_cropped_image, [largest_contour], -1, (0, 255, 0), 2)
                

                # 計算最大的輪廓的中心
                M = cv2.moments(largest_contour)
                if M["m00"] != 0:
                    cX = int(M["m10"] / M["m00"])
                    cY = int(M["m01"] / M["m00"])
                else:
                    cX, cY = 0, 0

                # 計算車道中心點與輪廓中心點的距離
                distance = np.sqrt((lane_cX - cX) ** 2 + (lane_cY - cY) ** 2)

                # print(f"車道中心點與輪廓中心點之間的距離: {distance}")
                # print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")

                # 繪製編號
                cv2.putText(new_cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
                in_lane = self.point_in_polygon(cX, cY, lane_polygon)
                if largest_contour_area > 300 and distance < 40:
                    # print(f"車道中心點與輪廓中心點之間的距離: {distance}")
                    # print("障礙物在車道內")
                    # print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")
                    print("發現障礙物")
                    self.write_file(file_path, obstacle)
                    self.stop_callback()
                else:
                    self.write_file(file_path, run)
                    self.resume_callback()
                # if in_lane:
                #     if largest_contour_area > 200 and distance < 50:
                #         print(f"車道中心點與輪廓中心點之間的距離: {distance}")
                #         print("障礙物在車道內")
                #         print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")
                #         print("發現障礙物")
                #         self.stop_callback()
                # else:
                    # print("障礙物在車道外")
                # 調整 original_cropped_image 的大小以匹配裁剪區域的大小
                # cropped_image = new_cropped_image
                # image[int(height * 0.4):, :] = cropped_image7
            cropped_image[min_y:max_y, min_x:max_x] = new_cropped_image
            image[int(height * 0.35):, int(width * 0.1):] = cropped_image

        return image


    # def stop_obstacle_image(self, image):
    #     height, width = image.shape[:2]

    #     # 裁剪圖像
    #     cropped_image = image[int(height * 0.4):, :]

    #     new_cropped_image = cropped_image.copy()

    #     # 檢測白線
    #     hsv = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    #     lower = np.array([0, 0, 200])
    #     upper = np.array([180, 30, 255])
    #     # upper = np.array([180, 30, 255])
    #     binary = cv2.inRange(hsv, lower, upper)
    #     edged = cv2.Canny(binary, 50, 150, apertureSize=3)
    #     kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    #     closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    #     lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 30, minLineLength=30, maxLineGap=10)
    #     # lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 30, minLineLength=30, maxLineGap=10)

    #     # 初始化變數
    #     min_x = min_y = 0
    #     max_x = 160
    #     max_y = 120

    #     # 在裁剪圖像上繪製白線
    #     if lines is not None:
    #         for line in lines:
    #             for x1, y1, x2, y2 in line:
    #                 cv2.line(cropped_image, (x1, y1), (x2, y2), (255, 0, 0), 2)
        

    #         # 找出所有紅線的x和y座標
    #         x_coords = []
    #         y_coords = []
    #         for line in lines:
    #             for x1, y1, x2, y2 in line:
    #                 x_coords.extend([x1, x2])
    #                 y_coords.extend([y1, y2])
            
    #         # 計算紅線圍成的矩形的邊界
    #         min_x = min(x_coords)
    #         max_x = max(x_coords)
    #         min_y = min(y_coords)
    #         max_y = max(y_coords)

    #         # 定義車道範圍多邊形
    #         lane_polygon = [(min_x, min_y), (max_x, min_y), (max_x, max_y), (min_x, max_y)]
            
    #         # 裁切影像
    #         new_cropped_image = new_cropped_image[min_y:max_y, min_x:max_x]
    #     else:
    #         new_cropped_image = new_cropped_image

    #     if new_cropped_image.size == 0:
    #         return image

    #     # 判斷障礙物
    #     gray = cv2.cvtColor(new_cropped_image, cv2.COLOR_BGR2GRAY)
    #     _, binary = cv2.threshold(gray, 105, 255, cv2.THRESH_BINARY)
        
    #     # 反轉二值化圖像
    #     binary_inv = cv2.bitwise_not(binary)
        
    #     # 找出反轉後的輪廓
    #     contours, _ = cv2.findContours(binary_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
    #     if contours:
    #         # 找到最大的輪廓
    #         largest_contour = max(contours, key=cv2.contourArea)
            
    #         # 計算最大的輪廓的面積
    #         largest_contour_area = cv2.contourArea(largest_contour)
            
    #         # 在終端機中打印輪廓大小和編號
    #         # print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")
            
    #         # 繪製最大的輪廓
    #         cv2.drawContours(new_cropped_image, [largest_contour], -1, (0, 255, 0), 2)
            
    #         # 計算最大的輪廓的中心
    #         M = cv2.moments(largest_contour)
    #         if M["m00"] != 0:
    #             cX = int(M["m10"] / M["m00"])
    #             cY = int(M["m01"] / M["m00"])
    #         else:
    #             cX, cY = 0, 0
            
    #         # 繪製編號
    #         cv2.putText(new_cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    #         in_lane = self.point_in_polygon(cX, cY, lane_polygon)
    #         if in_lane:
    #             if largest_contour_area > 600:
    #                 print("障礙物在車道內")
    #                 print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")
    #                 print("發現障礙物")
    #                 self.stop_callback()
    #         # else:
    #             # print("障礙物在車道外")
    #         # 調整 original_cropped_image 的大小以匹配裁剪區域的大小
    #         # cropped_image = new_cropped_image
    #         # image[int(height * 0.4):, :] = cropped_image7
            
    #         image[int(height * 0.4) + min_y:int(height * 0.4) + max_y, min_x:max_x] = new_cropped_image

    #     return image