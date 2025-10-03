import cv2
from face.detector import detect_face
from face.embedder import get_embedding
from face.utils import cosine_similarity
from db.database import get_students_by_class, insert_attendance
import numpy as np

def attendance(class_id, model_arcface, threshold=0.5):
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        return "Không thể mở camera!"

    face = detect_face(frame)
    if face is None:
        return "Không phát hiện khuôn mặt!"

    emb = get_embedding(face, model_arcface)

    students = get_students_by_class(class_id)
    best_match = None
    best_score = -1

    for student in students:
        emb_db = np.array(eval(student["embedding"]))
        score = cosine_similarity(emb, emb_db)
        if score > best_score:
            best_score = score
            best_match = student

    if best_score > threshold:
        insert_attendance(best_match["student_id"], class_id, "Thành công")
        return f"Điểm danh thành công: {best_match['name']} ({best_match['student_id']})"
    else:
        return "Điểm danh thất bại!"
