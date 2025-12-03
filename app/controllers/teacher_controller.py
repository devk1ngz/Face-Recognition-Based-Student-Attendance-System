from app.database.connector import get_session
from app.database.models import Course, Student, Attendance, User
from datetime import datetime
import cv2
import os
import numpy as np 
from insightface.app import FaceAnalysis
import pickle



face_app = FaceAnalysis(name='buffalo_l', providers=['CUDAExecutionProvider', 'CPUExecutionProvider'])
face_app.prepare(ctx_id=0, det_size=(640, 640))

CACHE_FILE = "data/face_data.pkl"


def get_teacher_detail(teacher_id):
    """Lấy thông tin chi tiết của giảng viên (SĐT, Email, ...)"""
    session = get_session()
    teacher = session.query(User).filter_by(id=teacher_id).first()
    if teacher:
        session.expunge(teacher)
    session.close()
    return teacher

def get_teaching_stats(teacher_id):
    """Lấy danh sách lớp đang dạy kèm sĩ số sinh viên"""
    session = get_session()
    courses = session.query(Course).filter_by(teacher_id=teacher_id).all()
    
    stats = []
    for c in courses:
        student_count = session.query(Student).filter_by(course_id=c.id).count()
        stats.append({
            "code": c.course_code,
            "name": c.course_name,
            "count": student_count
        })
    
    session.close()
    return stats

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                return pickle.load(f)
        except Exception:
            return {}
    return {}

def save_cache(data):
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(data, f)

def get_face_embedding(image):
    faces = face_app.get(image)
    if len(faces) > 0:
        return faces[0].embedding
    return None


def load_known_faces(course_id):
    """
    Kết hợp dữ liệu từ DB và Cache để trả về dữ liệu nhận diện.
    OUTPUT: trả về (embeddings, list_mssv, list_names)
    """
    print(f"Đang tải dữ liệu cho Course ID: {course_id}...")

    session = get_session()
    students_in_course = session.query(Student).filter_by(course_id=course_id).all()

    course_students_map = {s.mssv: s.name for s in students_in_course}
    session.close()
    

    cached_data = load_cache()
    
 
    if not cached_data:

        print("Cache trống, đang tái tạo từ thư mục dataset...")
        save_dir = "dataset"
        if os.path.exists(save_dir):
            for f in os.listdir(save_dir):
                if f.endswith(('.jpg', '.png')):
                    mssv_key = os.path.splitext(f)[0]
                    img = cv2.imread(os.path.join(save_dir, f))
                    if img is not None:
                        emb = get_face_embedding(img)
                        if emb is not None:
                            cached_data[mssv_key] = emb
            save_cache(cached_data)

 
    known_embeddings = []
    known_mssvs = [] 
    known_names = []

    for mssv, embedding in cached_data.items():
        if mssv in course_students_map:
            name = course_students_map[mssv]
            
            known_embeddings.append(embedding)
            known_mssvs.append(mssv)  
            known_names.append(name)

    print(f"Đã load {len(known_mssvs)} khuôn mặt cho lớp này.")
    return known_embeddings, known_mssvs, known_names

def get_teacher_courses(teacher_id):
    session = get_session()
    courses = session.query(Course).filter_by(teacher_id=teacher_id).all()
    session.expunge_all()
    session.close()
    return courses

def get_attendance_list(course_id, date_str):
    session = get_session()
    students = session.query(Student).filter_by(course_id=course_id).all()
    result = []
    for s in students:
        att = session.query(Attendance).filter_by(student_id=s.id, course_id=course_id, date=date_str).first()
        
        result.append({
            "id": s.id, 
            "mssv": s.mssv, 
            "name": s.name,
            "dob": str(s.dob) if s.dob else "",
            "class_name": s.class_name if hasattr(s, "class_name") else "", 
            "status": att.status if att else "Chưa điểm danh",
            "time": att.time if att else "--:--",
            "note": att.note if att else ""
        })
        
    session.close()
    return result

def update_attendance(mssv, course_id, date_str, status):
    """
    Nhận MSSV -> Tìm Student ID -> Cập nhật điểm danh
    """
    session = get_session()

    student = session.query(Student).filter_by(mssv=mssv, course_id=course_id).first()
    
    if not student:
        print(f"Không tìm thấy sinh viên có MSSV {mssv} trong lớp {course_id}")
        session.close()
        return

    student_id = student.id 

    att = session.query(Attendance).filter_by(student_id=student_id, course_id=course_id, date=date_str).first()
    
    if att:

        if att.status != "Có mặt": 
            att.status = status
            if status == "Có mặt" and att.time == "--:--":
                 att.time = datetime.now().strftime("%H:%M:%S")
    else:
        new_att = Attendance(
            student_id=student_id, 
            course_id=course_id, 
            date=date_str,
            time=datetime.now().strftime("%H:%M:%S") if status == "Có mặt" else "--:--", 
            status=status
        )
        session.add(new_att)
    
    session.commit()
    session.close()


def add_student(mssv, name, dob, class_name, course_id, frame):
    """
    Thêm sinh viên mới:
    1. Lưu vào DB.
    2. Lưu ảnh vào folder dataset (để backup).
    3. Tính vector và lưu vào cache (để dùng ngay).
    """
    session = get_session()

    exist = session.query(Student).filter_by(mssv=mssv).first()
    
    try:
        new_student = Student(mssv=mssv, name=name, dob=dob, class_name=class_name, course_id=course_id)
        session.add(new_student)
        session.flush() 
        student_id = new_student.id
        session.commit()

        save_dir = "dataset"
        if not os.path.exists(save_dir): os.makedirs(save_dir)
        
        img_path = os.path.join(save_dir, f"{mssv}.jpg")
        cv2.imwrite(img_path, frame)
        
        # TÍNH VECTOR VÀ LƯU CACHE
        embedding = get_face_embedding(frame)
        if embedding is not None:
            cache = load_cache()
            cache[mssv] = embedding 
            save_cache(cache)
            
        session.close()
        return True, "Thêm sinh viên thành công!"
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Lỗi: {str(e)}"
    

def import_student_from_excel(mssv, name, dob, class_name, course_id):
    session = get_session()
    try:
        exist = session.query(Student).filter_by(mssv=mssv, course_id=course_id).first()
        if exist:
            session.close()
            return False, f"MSSV {mssv} đã tồn tại trong lớp."

        new_student = Student(
            mssv=mssv, 
            name=name, 
            dob=dob, 
            class_name=class_name, 
            course_id=course_id
        )
        session.add(new_student)
        session.commit()
        session.close()
        return True, "Thành công"
        
    except Exception as e:
        session.rollback()
        session.close()
        return False, f"Lỗi Data: {str(e)}"

def create_or_get_course(course_code, course_name, teacher_id):
    session = get_session()
    course = session.query(Course).filter_by(course_code=course_code, teacher_id=teacher_id).first()
    
    if not course:
        course = Course(course_code=course_code, course_name=course_name, teacher_id=teacher_id, credits=3)
        session.add(course)
        session.commit()
        session.refresh(course)
        
    course_id = course.id
    session.close()
    return course_id