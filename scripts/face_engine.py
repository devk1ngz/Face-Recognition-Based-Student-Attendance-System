import os
import cv2
import pickle
import numpy as np
from insightface.app import FaceAnalysis

# --- CẤU HÌNH ---
DATASET_DIR = "data/raw_faces"      # Thư mục chứa ảnh gốc
CACHE_FILE = "data/face_data.pkl" # File lưu vector khuôn mặt

def main():
    # 1. Khởi tạo InsightFace (giống hệt trong teacher_controller)
    print("Đang khởi tạo model AI (InsightFace)...")
    face_app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
    face_app.prepare(ctx_id=0, det_size=(640, 640))

    # 2. Chuẩn bị biến lưu dữ liệu
    # Định dạng: { "MSSV": embedding_vector, ... }
    face_data = {}

    # Kiểm tra thư mục ảnh
    if not os.path.exists(DATASET_DIR):
        print(f"Lỗi: Không tìm thấy thư mục '{DATASET_DIR}'!")
        return

    # Lấy danh sách file ảnh
    files = os.listdir(DATASET_DIR)
    valid_files = [f for f in files if f.lower().endswith(('.jpg', '.png', '.jpeg'))]
    
    print(f"Tìm thấy {len(valid_files)} ảnh sinh viên. Bắt đầu xử lý...")

    count = 0
    for f in valid_files:
        # Lấy MSSV từ tên file (bỏ phần đuôi mở rộng)
        # Ví dụ: "2221050001.jpg" -> mssv = "2221050001"
        mssv = os.path.splitext(f)[0]
        
        path = os.path.join(DATASET_DIR, f)
        
        # Đọc ảnh
        img = cv2.imread(path)
        if img is None:
            print(f"[-] Không đọc được ảnh: {f}")
            continue

        # Trích xuất vector (embedding)
        faces = face_app.get(img)
        
        if len(faces) == 0:
            print(f"[-] Cảnh báo: Không tìm thấy khuôn mặt nào trong ảnh {f}")
        elif len(faces) > 1:
            print(f"[-] Cảnh báo: Ảnh {f} có nhiều hơn 1 khuôn mặt. Lấy khuôn mặt to nhất.")
            face_data[mssv] = faces[0].embedding
            count += 1
        else:
            # Trường hợp hoàn hảo: 1 khuôn mặt
            face_data[mssv] = faces[0].embedding
            count += 1
            print(f"[+] Đã xử lý: {mssv}")

    # 3. Lưu xuống file .pkl
    if count > 0:
        print("------------------------------------------------")
        print(f"Đang lưu dữ liệu của {count} sinh viên vào file '{CACHE_FILE}'...")
        with open(CACHE_FILE, 'wb') as f:
            pickle.dump(face_data, f)
        print("XONG! Bạn có thể bắt đầu điểm danh ngay.")
    else:
        print("Không có dữ liệu nào được lưu.")

if __name__ == "__main__":
    main()