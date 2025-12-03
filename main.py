import sys
from PyQt5.QtWidgets import QApplication
from app.database.connector import init_db
from app.ui.login import LoginWindow
from app.ui.teacher_window import TeacherWindow
from app.ui.student_window import StudentWindow

def main():
    init_db()
    app = QApplication(sys.argv)
    
    login_window = LoginWindow()
    teacher_window = None 
    student_window = None 
    
    def show_dashboard():
        nonlocal teacher_window, student_window
        role = login_window.user_role
        curr_user = login_window.current_user_info
        uid = curr_user['id'] if curr_user else None

        if role == "teacher":
            teacher_window = TeacherWindow(teacher_id=uid)
            if curr_user: teacher_window.set_teacher_info(curr_user['fullname'], curr_user['code'])
            teacher_window.showMaximized()
            teacher_window.btn_logout.clicked.connect(logout)
            login_window.close()
            
        elif role == "student":
            student_window = StudentWindow(user_id=uid)
            student_window.showMaximized()
            student_window.btn_logout.clicked.connect(logout)
            login_window.close()

    def logout():
        nonlocal teacher_window, student_window
        if teacher_window: teacher_window.close(); teacher_window = None
        if student_window: student_window.close(); student_window = None
        login_window.show(); login_window.password.clear()

    login_window.btn_login.clicked.connect(lambda: login_window.validate_login() and show_dashboard())
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()