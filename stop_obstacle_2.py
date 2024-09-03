"""
使用即時影像測試是否能判斷障礙物+偵測道路改良版+判斷障礙物是否在車道內
"""
import cv2
import numpy as np
import time
from donkeycar.parts.camera import PiCamera # type: ignore

def detect_white_lines(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 0, 200])
    upper = np.array([180, 30, 255])
    binary = cv2.inRange(hsv, lower, upper)
    edged = cv2.Canny(binary, 50, 150, apertureSize=3)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)
    lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 30, minLineLength=30, maxLineGap=10)
    return lines, closed

def point_in_polygon(x, y, polygon):
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

def stop_obstacle(image):
    height, width = image.shape[:2]
    cropped_image = image[int(height * 0.4):, :]
    # height, width, _ = image.shape
    # top_crop = int(height * 0.4)
    # bottom_crop = int(height * 1)
    # left_crop = int(width * 0.1)
    # right_crop = int(width * 0.9)
    
    # # 裁剪圖像
    # cropped_image = image[top_crop:bottom_crop, left_crop:right_crop]
    
    original_cropped_image = cropped_image.copy()

    # 檢測白線
    lines, edges = detect_white_lines(cropped_image)
    
    # 在裁剪圖像上繪製白線
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(cropped_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
    

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
        original_cropped_image = original_cropped_image[min_y:max_y, min_x:max_x]
    else:
        original_cropped_image = original_cropped_image

    # 判斷障礙物
    gray = cv2.cvtColor(original_cropped_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
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
        cv2.drawContours(original_cropped_image, [largest_contour], -1, (0, 255, 0), 2)
        
        # 計算最大的輪廓的中心
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        
        # 繪製編號
        cv2.putText(original_cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
        in_lane = point_in_polygon(cX, cY, lane_polygon)
        if in_lane:
            print("障礙物在車道內")
            if largest_contour_area > 850:
                print("發現障礙物")
        else:
            print("障礙物在車道外")

    return edges, cropped_image, binary_inv

    # # 定義白線之間的範圍
    # if lines is not None:
    #     x_coords = []
    #     for line in lines:
    #         for x1, y1, x2, y2 in line:
    #             x_coords.append(x1)
    #             x_coords.append(x2)
    #     x_coords = np.array(x_coords)
    #     left_boundary = max(np.percentile(x_coords, 25), int(width * 0.1))
    #     right_boundary = min(np.percentile(x_coords, 75), int(width * 0.9))
    # else:
    #     left_boundary = int(width * 0.1)
    #     right_boundary = int(width * 0.9)
    
    # # 進一步裁剪圖像
    # further_cropped_image = image[:, int(left_boundary):int(right_boundary)]
    
    # gray = cv2.cvtColor(further_cropped_image, cv2.COLOR_BGR2GRAY)
    # _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # # 反轉二值化圖像
    # binary_inv = cv2.bitwise_not(binary)
    
    # # 找出反轉後的輪廓
    # contours, _ = cv2.findContours(binary_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    # if contours:
    #     # 找到最大的輪廓
    #     largest_contour = max(contours, key=cv2.contourArea)
        
    #     # 計算最大的輪廓的面積
    #     largest_contour_area = cv2.contourArea(largest_contour)
        
    #     # 在終端機中打印輪廓大小和編號
    #     print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")
        
    #     # 繪製最大的輪廓
    #     cv2.drawContours(further_cropped_image, [largest_contour], -1, (0, 255, 0), 2)
        
    #     # 計算最大的輪廓的中心
    #     M = cv2.moments(largest_contour)
    #     if M["m00"] != 0:
    #         cX = int(M["m10"] / M["m00"])
    #         cY = int(M["m01"] / M["m00"])
    #     else:
    #         cX, cY = 0, 0
        
    #     # 繪製編號
    #     cv2.putText(further_cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    #     if largest_contour_area > 500:
    #         print("發現障礙物")

    # 在原圖像上顯示裁剪區域的輪廓
    # image[:, int(left_boundary):int(right_boundary)] = further_cropped_image
    # image[top_crop:bottom_crop, left_crop:right_crop] = cropped_image

    # return edges, image

def main():
    cam = PiCamera()
    cam.resolution = (160, 120)
    
    while True:
        image = cam.run()
        edges, image, binary_inv = stop_obstacle(image)

        cv2.imshow("Camera View", image)
        cv2.imshow("Edges", edges)
        cv2.imshow("binary_inv", binary_inv)
        time.sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()
