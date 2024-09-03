"""
使用即時影像測試是否能判斷障礙物
"""
import cv2
import numpy as np
import time
from donkeycar.parts.camera import PiCamera

def stop_obstacle(image):
    height, width, _ = image.shape
    top_crop = int(height * 0.3)
    bottom_crop = int(height * 0.9)
    left_crop = int(width * 0.3)
    right_crop = int(width * 0.7)
    
    # 裁剪圖像
    cropped_image = image[top_crop:bottom_crop, left_crop:right_crop]
    
    gray = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    
    # 反轉二值化圖像
    binary_inv = cv2.bitwise_not(binary)
    
    # 找出反轉後的輪廓
    contours, hierarchy = cv2.findContours(binary_inv, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # 在裁剪區域上繪製編號
    for i, contour in enumerate(contours):
        # 找到最大的輪廓
        largest_contour = max(contours, key=cv2.contourArea)
        
        # 計算最大的輪廓的面積
        largest_contour_area = cv2.contourArea(largest_contour)

        print(f"輪廓編號: 1, 輪廓大小: {largest_contour_area}")

        # 繪製最大的輪廓
        cv2.drawContours(cropped_image, [largest_contour], -1, (0, 255, 0), 2)
        
        # 計算最大的輪廓的中心
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
        else:
            cX, cY = 0, 0
        
        # 繪製編號
        cv2.putText(cropped_image, "1", (cX, cY), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # 在原圖像上顯示裁剪區域的輪廓
    image[top_crop:bottom_crop, left_crop:right_crop] = cropped_image

    return binary, image

    # # 畫出所有輪廓
    # cv2.drawContours(cropped_image, contours, -1, (0, 255, 0), 2)
    
    # # 在原圖像上顯示裁剪區域的輪廓
    # image[top_crop:bottom_crop, :] = cropped_image

    # return binary, image


    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    (_, binary) = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
    (contours, hierarchy) = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    if len(contours) == 0:
        return False, image

    cnt = contours[0]

    ((x, y), radius) = cv2.minEnclosingCircle(cnt)
    M = cv2.moments(cnt)

    if M["m00"] == 0:
        return False, image

    center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
    cv2.circle(image, (int(x), int(y)), int(radius), (0, 255, 255), 2)
    cv2.circle(image, center, 5, (0, 0, 255), -1)

    stop_sign = False
    return binary, image
    """


def main():
    cam = PiCamera()
    cam.resolution = (160, 120)
    
    while True:
        image = cam.run()
        # stop_sign, annotated_image = stop_obstacle(image)
        binary, annotated_image = stop_obstacle(image)

        # if stop_sign:
        #     print("偵測到障礙物")
        # else:
        #     print("未偵測到障礙物")
        cv2.imshow("binary", binary)
        cv2.imshow("Camera View", annotated_image)
        time.sleep(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()