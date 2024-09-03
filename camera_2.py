"""
校正魚眼鏡頭，並產生校正值，將影像大小改為160x120
"""
import numpy as np
import cv2
import glob

# 設置棋盤格尺寸（內部角點數量，通常為棋盤格行數-1 x 列數-1）
chessboard_size = (9, 6)
square_size = 1.0  # 實際方格邊長（例如 1.0 cm）

# 準備世界坐標系中的棋盤格點 (0,0,0), (1,0,0), (2,0,0), ...
objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp = objp * square_size

# 存儲棋盤格角點的世界坐標和圖像坐標對
objpoints = []  # 在世界坐標系中的3D點
imgpoints = []  # 在圖像平面的2D點

# 讀取所有棋盤格圖片
images = glob.glob('chessboard/*.jpg')

def resize_image(image, size=(160, 120)):
    """將影像縮放為指定大小。"""
    return cv2.resize(image, size, interpolation=cv2.INTER_LINEAR)

for fname in images:
    img = cv2.imread(fname)
    if img is None:
        print(f"Error: Unable to load image {fname}")
        continue

    # 將影像大小改為160x120
    img = resize_image(img, size=(160, 120))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # 找到棋盤格角點
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
    
    # 如果找到足夠點數，則添加到點集合
    if ret:
        objpoints.append(objp)
        imgpoints.append(corners)
        
        # 可視化角點
        cv2.drawChessboardCorners(img, chessboard_size, corners, ret)
        cv2.imshow('img', img)
        cv2.waitKey(500)

cv2.destroyAllWindows()

# 執行相機校正
ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# 打印相機矩陣和畸變係數
print("Camera matrix:")
print(camera_matrix)
print("Distortion coefficients:")
print(dist_coeffs)

# 儲存校正結果
np.savez("calibration_data_160x120.npz", camera_matrix=camera_matrix, dist_coeffs=dist_coeffs)

# 進行影像校正
img = cv2.imread('chessboard/1.jpg')  # 使用其中一張棋盤格照片作為範例
if img is None:
    print("Error: Unable to load image for distortion correction.")
else:
    # 將影像大小改為160x120
    img = resize_image(img, size=(160, 120))
    h, w = img.shape[:2]
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))
    undistorted_img = cv2.undistort(img, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # 裁剪影像
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]

    # 顯示校正前後的影像
    cv2.imshow('Original Image', img)
    cv2.imshow('Undistorted Image', undistorted_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
