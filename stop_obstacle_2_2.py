"""
使用即時影像測試是否能判斷障礙物+偵測道路改良版+判斷障礙物是否在車道內+修改回傳影像(改良版)
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
    lines = cv2.HoughLinesP(closed, 1, np.pi / 180, 30, minLineLength=20, maxLineGap=10)
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
    
    original_cropped_image = cropped_image.copy()

    # 檢測白線
    lines, edges = detect_white_lines(cropped_image)
    
    # 在裁剪圖像上繪製白線
    if lines is not None:
        for line in lines:
            for x1, y1, x2, y2 in line:
                cv2.line(cropped_image, (x1, y1), (x2, y2), (200, 200, 200), 2)
    

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

        # 判斷障礙物
        gray = cv2.cvtColor(new_cropped_image, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, 90, 255, cv2.THRESH_BINARY)
        
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
            cv2.drawContours(new_cropped_image, [largest_contour], -1, (0, 255, 0), 2)
            
            # 計算最大的輪廓的中心
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
            else:
                cX, cY = 0, 0
            
            # 繪製編號
            cv2.putText(new_cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            in_lane = point_in_polygon(cX, cY, lane_polygon)
            if in_lane:
                print("障礙物在車道內")
                if largest_contour_area > 600:
                    print("發現障礙物")
            else:
                print("障礙物在車道外")

        cropped_image[min_y:max_y, min_x:max_x] = new_cropped_image
        image[int(height * 0.4):, :] = cropped_image

    return edges, image, binary_inv

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
