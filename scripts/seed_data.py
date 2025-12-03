import sys
import os
import random
from datetime import date, timedelta

# --- CẤU HÌNH ĐƯỜNG DẪN ---
current_dir = os.path.dirname(os.path.abspath(__file__)) 
project_root = os.path.dirname(current_dir)              
sys.path.append(project_root)

from app.database.connector import init_db, get_session
from app.database.models import User, Course, Student

# --- DỮ LIỆU MẪU ---
HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ", "Hồ", "Ngô", "Dương", "Lý"]
DEM = ["Văn", "Thị", "Minh", "Đức", "Ngọc", "Xuân", "Thanh", "Hữu", "Gia", "Khánh", "Tuấn", "Hoài", "Quốc", "Mạnh", "Thùy", "Phương"]
TEN = ["Anh", "Bảo", "Châu", "Dũng", "Em", "Giang", "Hà", "Hải", "Hiếu", "Hòa", "Hùng", "Huy", "Khánh", "Khoa", "Lâm", "Linh", "Long", "Minh", "Nam", "Nga", "Nhi", "Phát", "Phúc", "Quân", "Quỳnh", "Sơn", "Thảo", "Thắng", "Thịnh", "Trang", "Trung", "Tú", "Tùng", "Việt", "Vinh", "Uyên", "Yến"]

CLASSES_ADMIN = ["DCCTCT67A", "DCCTCT67B"]

# Đường dẫn thư mục chứa ảnh raw
RAW_FACES_DIR = os.path.join(project_root, "data", "raw_faces")

def generate_random_name():
    return f"{random.choice(HO)} {random.choice(DEM)} {random.choice(TEN)}"

def get_random_dob_2004():
    start_date = date(2004, 1, 1)
    end_date = date(2004, 12, 31)
    return start_date + timedelta(days=random.randrange((end_date - start_date).days))

def generate_phone():
    """Sinh SĐT ngẫu nhiên cho Giảng viên"""
    prefixes = ["090", "091", "098", "097", "089"]
    suffix = "".join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{random.choice(prefixes)}{suffix}"

def check_student_avatar(mssv):
    """
    Kiểm tra xem sinh viên có ảnh trong data/raw_faces hay không.
    Ưu tiên .jpg rồi đến .png
    """
    if not os.path.exists(RAW_FACES_DIR):
        return None
        
    # Các đuôi file ảnh chấp nhận
    extensions = [".jpg", ".png", ".jpeg"]
    
    for ext in extensions:
        file_name = f"{mssv}{ext}"
        full_path = os.path.join(RAW_FACES_DIR, file_name)
        
        if os.path.exists(full_path):
            # Trả về đường dẫn tương đối để lưu vào DB (dễ dùng cho API/Frontend)
            # Ví dụ: /data/raw_faces/2221050001.jpg
            return f"/data/raw_faces/{file_name}"
            
    return None

def seed():
    print("🔄 Đang khởi tạo Database...")
    
    # Tạo thư mục raw_faces nếu chưa có (để tránh lỗi code, dù chưa có ảnh)
    if not os.path.exists(RAW_FACES_DIR):
        os.makedirs(RAW_FACES_DIR)
        print(f"⚠️ Đã tạo thư mục trống: {RAW_FACES_DIR}. Hãy bỏ ảnh vào đây nếu muốn import.")

    init_db() 
    session = get_session()

    # 1. TẠO GIÁO VIÊN
    print("Creating Teachers...")
    teachers_data = [
        {
            "u": "admin", 
            "n": "ThS. Đặng Văn Nam", 
            "c": "GV001", 
            "email": "dangvannam@humg.edu.vn", # <--- Thêm mail
            "avt": "/home/namvh/Downloads/Face-Recognition-Based-Student-Attendance-System/assets/img/teacher/gv001.jpg"
        },
        {
            "u": "gv002", 
            "n": "ThS. Nguyễn Thùy Dương", 
            "c": "GV002", 
            "email": "nguyenthuyduong@humg.edu.vn", # <--- Thêm mail
            "avt": "/home/namvh/Downloads/Face-Recognition-Based-Student-Attendance-System/assets/img/teacher/gv002.jpg"
        }
    ]

    for t in teachers_data:
        if not session.query(User).filter_by(username=t["u"]).first():
            gv = User(
                username=t["u"], password="123", fullname=t["n"], user_code=t["c"], role="teacher",
                phone_number=generate_phone(),
                avatar=t["avt"],
                email=t["email"]
            )
            session.add(gv)
    session.commit()
    
    gv1 = session.query(User).filter_by(username="admin").first()
    gv2 = session.query(User).filter_by(username="gv002").first()

    # 2. TẠO LỚP HỌC PHẦN
    print("Creating Courses...")
    courses_data = [
        {"code": "7080518", "name": "Thị giác máy tính", "teacher": gv1, "credits": 3},
        {"code": "7080122", "name": "Trí tuệ nhân tạo", "teacher": gv1, "credits": 4},
        {"code": "7080116", "name": "Lập trình Web nâng cao", "teacher": gv2, "credits": 3},
        {"code": "7080514", "name": "Internet vạn vật (IoT)", "teacher": gv2, "credits": 2},
    ]
    
    course_objects = []
    for c_data in courses_data:
        existing = session.query(Course).filter_by(course_code=c_data["code"]).first()
        if not existing:
            course = Course(course_code=c_data["code"], course_name=c_data["name"], teacher_id=c_data["teacher"].id)
            session.add(course)
            session.commit()
            course_objects.append(course)
            credits=c_data["credits"]
        else:
            course_objects.append(existing)

    # 3. TẠO SINH VIÊN
    print("Creating Students...")
    counter = 1 
    total_new = 0
    count_with_avatar = 0
    
    for course in course_objects:
        num_students = random.randint(15, 20)
        print(f" -> Lớp HP {course.course_name}: Thêm {num_students} sinh viên.")
        
        for _ in range(num_students):
            mssv = f"222105{counter:04d}"
            
            if session.query(User).filter_by(username=mssv).first():
                counter += 1
                continue

            name = generate_random_name()
            
            # --- LOGIC XỬ LÝ AVATAR SINH VIÊN ---
            # Kiểm tra xem có file ảnh trùng tên MSSV không
            student_avatar_path = check_student_avatar(mssv)
            if student_avatar_path:
                count_with_avatar += 1
            # ------------------------------------
            email_sv = f"{mssv}@humg.edu.vn"
            user_sv = User(
                username=mssv, password="123", fullname=name, user_code=mssv, role="student"
                # User SV không cần phone và avatar (để null)
            )
            session.add(user_sv)
            session.commit() 
            
            student = Student(
                mssv=mssv, name=name, dob=get_random_dob_2004(),          
                class_name=random.choice(CLASSES_ADMIN), 
                course_id=course.id,
                user_id=user_sv.id,
                avatar=student_avatar_path,
                email=email_sv
            )
            session.add(student)
            
            counter += 1
            total_new += 1

    session.commit()
    session.close()
    
    print("-" * 50)
    print(f"✅ XONG! Đã thêm {total_new} sinh viên.")
    print(f"📸 Tìm thấy {count_with_avatar} sinh viên có ảnh sẵn trong 'data/raw_faces'.")
    print("-" * 50)

if __name__ == "__main__":
    seed()