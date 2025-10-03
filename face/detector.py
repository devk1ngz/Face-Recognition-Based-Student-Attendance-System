from retinaface import RetinaFace
import cv2

def detect_face(image):
    faces = RetinaFace.detect_faces(image)
    if isinstance(faces, dict) and len(faces) > 0:
        face_key = list(faces.keys())[0]
        facial_area = faces[face_key]['facial_area']
        x1, y1, x2, y2 = facial_area
        return image[y1:y2, x1:x2]
    return None
