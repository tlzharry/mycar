"""
影像學練習
"""

import cv2
import numpy as np

image = cv2.imread("data/tub_33_24-07-22/images/56_cam_image_array_.jpg")
h, s, v = 100, 100, 100
def nothing(pos): pass
cv2.namedWindow('hsv_demo')
cv2.createTrackbar('hl', 'hsv_demo', 0, 255, nothing)
cv2.createTrackbar('hu', 'hsv_demo', 255, 255, nothing)
cv2.createTrackbar('sl', 'hsv_demo', 0, 255, nothing)
cv2.createTrackbar('su', 'hsv_demo', 255, 255, nothing)
cv2.createTrackbar('vl', 'hsv_demo', 0, 255, nothing)
cv2.createTrackbar('vu', 'hsv_demo', 255, 255, nothing)

while True:
    hl = cv2.getTrackbarPos('hl', 'hsv_demo')
    hu = cv2.getTrackbarPos('hu', 'hsv_demo')
    sl = cv2.getTrackbarPos('sl', 'hsv_demo')
    su = cv2.getTrackbarPos('su', 'hsv_demo')
    vl = cv2.getTrackbarPos('vl', 'hsv_demo')
    vu = cv2.getTrackbarPos('vu', 'hsv_demo')
    
    # cv2.imshow("Normal", image)

    # gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # cv2.imshow("Gray", gray)

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # cv2.imshow("HSV", hsv)
    

    #顯示影像
    # cv2.imshow("line", image_copy)
    
    lower = np.array( [hl, sl, vl] )
    upper = np.array( [hu, su, vu] )
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)
    cv2.imshow("hsv_demo", result)
    

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()