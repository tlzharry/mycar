"""
使用校正值校正魚眼鏡頭
"""

import cv2
import numpy as np

def load_calibration_data(file_path):
    """從檔案中讀取相機校正數據。"""
    with np.load(file_path) as data:
        camera_matrix = data['camera_matrix']
        dist_coeffs = data['dist_coeffs']
    return camera_matrix, dist_coeffs

def apply_calibration(image_path, calibration_data_path):
    """將校正數據應用於影像並顯示結果。"""
    # 讀取校正數據
    camera_matrix, dist_coeffs = load_calibration_data(calibration_data_path)

    # 讀取待校正影像
    image = cv2.imread(image_path)
    if image is None:
        print("Error: Image not found or unable to load.")
        return

    # 取得影像的尺寸
    h, w = image.shape[:2]

    # 計算新的相機矩陣
    new_camera_matrix, roi = cv2.getOptimalNewCameraMatrix(camera_matrix, dist_coeffs, (w, h), 1, (w, h))

    # 應用校正
    undistorted_img = cv2.undistort(image, camera_matrix, dist_coeffs, None, new_camera_matrix)

    # 裁剪影像
    x, y, w, h = roi
    undistorted_img = undistorted_img[y:y+h, x:x+w]

    # 將影像調整到目標尺寸
    target_size = (160, 120)
    resized_img = cv2.resize(undistorted_img, target_size)

    # 顯示影像
    cv2.imshow("Original Image", image)
    cv2.imshow("Undistorted Image", resized_img)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

# 主程式
if __name__ == "__main__":
    image_path = "data/tub_33_24-07-22/images/146_cam_image_array_.jpg"  # 替換為你的影像路徑
    calibration_data_path = "calibration_data_160x120.npz"  # 替換為你的校正數據檔案路徑
    apply_calibration(image_path, calibration_data_path)
