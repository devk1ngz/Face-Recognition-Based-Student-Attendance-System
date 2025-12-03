from app.database.connector import get_session
from app.database.models import Student, Attendance, User, Course 

def get_student_by_user_id(user_id):
    session = get_session()
    student = session.query(Student).filter_by(user_id=user_id).first()
    
    if student:
        session.expunge(student)
        session.close()
        return student
    
    user = session.query(User).filter_by(id=user_id).first()
    if user:
        class TempStudent:
            def __init__(self, name, mssv, id):
                self.name = name
                self.mssv = mssv
                self.id = id 
                self.course = None 

        temp_student = TempStudent(name=user.fullname, mssv=user.user_code, id=None)
        session.close()
        return temp_student

    session.close()
    return None

def get_student_courses(student_id):
    session = get_session()
    student = session.query(Student).filter_by(id=student_id).first()
    courses = []

    if student and student.course:
        session.expunge(student.course)
        courses.append(student.course)
    
    session.close()
    return courses
def get_student_course_details(student_id):
    """
    Trả về danh sách các lớp sinh viên đang học, kèm thông tin giảng viên.
    """
    session = get_session()
    student = session.query(Student).filter_by(id=student_id).first()
    
    results = []

    if student and student.course:
        c = student.course

        teacher_name = "Chưa cập nhật"
        teacher_phone = "Chưa có SĐT"
        
        if c.teacher:
            teacher_name = c.teacher.fullname if c.teacher.fullname else teacher_name
            teacher_phone = c.teacher.phone_number if c.teacher.phone_number else teacher_phone
            
        results.append({
            "course_name": c.course_name,
            "course_code": c.course_code,
            "teacher_name": teacher_name,
            "teacher_phone": teacher_phone
        })
        
    session.close()
    return results


def get_student_attendance_history(student_id, course_id):
    session = get_session()

    course = session.query(Course).filter_by(id=course_id).first()
    
    t_name = "---"
    t_phone = "---"
    
    if course and course.teacher:
        t_name = course.teacher.fullname if course.teacher.fullname else "Chưa cập nhật"
        t_phone = course.teacher.phone_number if course.teacher.phone_number else "Chưa có SĐT"

    attendances = session.query(Attendance).filter_by(
        student_id=student_id, 
        course_id=course_id
    ).order_by(Attendance.date.desc()).all()

    result = []
    for a in attendances:
        result.append({
            "date": a.date,
            "time": a.time,
            "status": a.status,
            "note": a.note,
            "teacher_name": t_name,   
            "teacher_phone": t_phone  
        })
        
    session.close()
    return result