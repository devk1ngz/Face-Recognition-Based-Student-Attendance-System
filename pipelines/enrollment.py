import cv2
from face.detector import detect_face
from face.embedder import get_embedding
from db.database import insert_student

def enroll_student(student_id, name, class_id, image_path, model_arcface):
    img = cv2.imread(image_path)
    face = detect_face(img)
    if face is None:
        print(f"Không tìm thấy khuôn mặt trong ảnh {image_path}")
        return
    embedding = get_embedding(face, model_arcface)
    insert_student(student_id, name, class_id, embedding)
    print(f"Đã lưu sinh viên {name} ({student_id}) vào DB")
