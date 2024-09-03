"""
使用照片測試是否能判斷出停止線
"""
import cv2
import numpy as np

image = cv2.imread("data/tub_33_24-07-22/images/888_cam_image_array_.jpg")
if image is None:
    print("Error: Image not found or unable to read.")
    exit()

# 將影像轉換為HSV
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# 定義白色HSV範圍
# lower = np.array( [91, 0, 196] )
# upper = np.array( [139, 255, 255] )
# lower = np.array( [82, 0, 170] )
# upper = np.array( [147, 255, 255] )
lower = np.array([0, 0, 200])
upper = np.array([170, 25, 255])

# 篩選出白色區域
binary = cv2.inRange(hsv, lower, upper)

# 使用邊緣檢測
edged = cv2.Canny(binary, 50, 150)

# 使用形態學操作去除小的噪點
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
closed = cv2.morphologyEx(edged, cv2.MORPH_CLOSE, kernel)

lines = cv2.HoughLinesP(closed, 1, np.pi/180, 50, minLineLength=100, maxLineGap=50)

if lines is not None:
    for line in lines:
        for x1, y1, x2, y2 in line:
            angle = np.degrees(np.arctan2(y2 - y1, x2 - x1))
            print(f"Line: ({x1}, {y1}) -> ({x2}, {y2}), Angle: {angle}")
            if -6 <= angle <= 6:
                print("yes")
                # 畫出檢測到的線條
                cv2.line(image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            else:
                print("No line")
                cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
else:
    print("No line in this picture")
#顯示影像
cv2.imshow("edged", edged)
cv2.imshow("line", image)

cv2.waitKey(0)

cv2.destroyAllWindows()