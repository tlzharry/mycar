"""
使用即時影像測試是否能判斷停止線
"""

import cv2
import numpy as np
import time
from donkeycar.parts.camera import PiCamera

def detect_stop_line(image):
    # 設定ROI，只關注畫面下方30%
    # roi = image[int(image.shape[0] * 0.3):, :]
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

    # 尋找影像中的線條
    lines = cv2.HoughLinesP(closed, 1, np.pi/180, 50, maxLineGap=50)
    
    stop_line_detected = False
    if lines is not None:
        count = 0
        for line in lines:
            for x1, y1, x2, y2 in line:
                y1 += roi_start
                y2 += roi_start
                # y1 += int(image.shape[0] * 0.3)
                # y2 += int(image.shape[0] * 0.3)
                # 畫出檢測到的線條
                angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
                count+=1
                # 檢測到白色橫線
                if -3 <= angle <= 3:  # 檢查是否為橫線並且位於畫面下方
                    print(f"Line: ({x1}, {y1}) -> ({x2}, {y2}), Angle: {angle}")
                    if count >= 2:
                        stop_line_detected = True
    return stop_line_detected, image, closed

def main():
    # 初始化相機
    cam = PiCamera()
    cam.resolution =(160, 120)

    while True:
        # 獲取相機影像
        image = cam.run()
        # 檢測停止線
        stop_line_detected, annotated_image, closed_image = detect_stop_line(image)
        
        if stop_line_detected:
            print("偵測到白色橫線")
        else:
            print("未偵測到白色橫線")

        # 顯示相機影像
        cv2.imshow('Camera View', annotated_image)
        cv2.imshow('closed', closed_image)

        # 按下 'q' 鍵退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 間隔2秒
        # time.sleep(2)

    # 釋放資源
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()