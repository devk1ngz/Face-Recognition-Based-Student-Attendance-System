import os
from PyQt5.QtWidgets import (QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QFrame, QGraphicsDropShadowEffect, 
                             QMessageBox, QRadioButton, QButtonGroup) 
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon
from app.config import STYLES_DIR, IMG_DIR
from app.controllers.auth_controller import register_user

class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đăng Ký Tài Khoản")
        self.setFixedSize(1000, 750)
        self.btn_back = QPushButton("Đã có tài khoản? Quay lại đăng nhập") 
        self.pass_hidden = True; self.confirm_hidden = True
        self.initUI(); self.load_style(); self.set_window_icon()

    def set_window_icon(self):
        p = os.path.join(IMG_DIR, "logo_humg.jpg")
        if os.path.exists(p): self.setWindowIcon(QIcon(p))

    def load_style(self):
        p = os.path.join(STYLES_DIR, "register_style.qss")
        if os.path.exists(p): 
            with open(p, "r", encoding="utf-8") as f: self.setStyleSheet(f.read())

    def initUI(self):
        ml = QVBoxLayout(); self.setLayout(ml)
        self.card = QFrame(); self.card.setObjectName("register_card")
        sh = QGraphicsDropShadowEffect(); sh.setBlurRadius(25); sh.setYOffset(5); sh.setColor(QColor(0,0,0,50)); self.card.setGraphicsEffect(sh)
        cl = QVBoxLayout(); cl.setContentsMargins(50,30,50,30); cl.setSpacing(15); self.card.setLayout(cl)

        logo = QLabel(); logo.setAlignment(Qt.AlignCenter); logo.setFixedHeight(70)
        lp = os.path.join(IMG_DIR, "logo_humg.jpg")
        if os.path.exists(lp): logo.setPixmap(QPixmap(lp).scaled(70,70,Qt.KeepAspectRatio,Qt.SmoothTransformation))

        t = QLabel("TẠO TÀI KHOẢN"); t.setObjectName("title"); t.setAlignment(Qt.AlignCenter)
        st = QLabel("Điền thông tin đăng ký"); st.setObjectName("subtitle"); st.setAlignment(Qt.AlignCenter)

        self.fullname = QLineEdit(); self.fullname.setPlaceholderText("Họ và tên"); self.fullname.setFixedHeight(45)
        
        self.staff_id = QLineEdit(); self.staff_id.setPlaceholderText("Mã Sinh viên / Mã Giáo viên"); self.staff_id.setFixedHeight(45)
        
        self.email = QLineEdit(); self.email.setPlaceholderText("Email"); self.email.setFixedHeight(45)
        
        self.password = QLineEdit(); self.password.setPlaceholderText("Mật khẩu"); self.password.setEchoMode(QLineEdit.Password); self.password.setFixedHeight(45)
        self.setup_eye(self.password, False)
        
        self.password_confirm = QLineEdit(); self.password_confirm.setPlaceholderText("Nhập lại mật khẩu"); self.password_confirm.setEchoMode(QLineEdit.Password); self.password_confirm.setFixedHeight(45)
        self.setup_eye(self.password_confirm, True)

        role_layout = QHBoxLayout()
        role_label = QLabel("Bạn là: ")
        self.rb_student = QRadioButton("Sinh viên")
        self.rb_teacher = QRadioButton("Giáo viên")
        self.rb_student.setChecked(True) 

        self.role_group = QButtonGroup(self)
        self.role_group.addButton(self.rb_student)
        self.role_group.addButton(self.rb_teacher)
        
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.rb_student)
        role_layout.addWidget(self.rb_teacher)
        role_layout.addStretch()
        # ---------------------------------------

        self.btn_reg = QPushButton("ĐĂNG KÝ NGAY"); self.btn_reg.setObjectName("btn_register"); self.btn_reg.setCursor(Qt.PointingHandCursor); self.btn_reg.setFixedHeight(50)
        self.btn_back.setObjectName("btn_back"); self.btn_back.setCursor(Qt.PointingHandCursor)

        cl.addWidget(logo); cl.addWidget(t); cl.addWidget(st); cl.addSpacing(5)
        cl.addWidget(self.fullname)
        cl.addWidget(self.staff_id) 
        cl.addWidget(self.email)

        cl.addLayout(role_layout)
        
        cl.addWidget(self.password); cl.addWidget(self.password_confirm)
        cl.addSpacing(10); cl.addWidget(self.btn_reg); cl.addWidget(self.btn_back)

        ml.addStretch(); ml.addWidget(self.card, alignment=Qt.AlignCenter); ml.addStretch()
        self.btn_reg.clicked.connect(self.handle_register)

    def setup_eye(self, le, is_c):
        o = QIcon(os.path.join(IMG_DIR, "eye.png")); c = QIcon(os.path.join(IMG_DIR, "eye_close.png"))
        act = le.addAction(c, QLineEdit.TrailingPosition)
        act.triggered.connect(lambda: self.toggle(le, act, o, c, is_c))

    def toggle(self, le, act, o, c, is_c):
        if is_c: self.confirm_hidden = not self.confirm_hidden; h = self.confirm_hidden
        else: self.pass_hidden = not self.pass_hidden; h = self.pass_hidden
        le.setEchoMode(QLineEdit.Password if h else QLineEdit.Normal)
        act.setIcon(c if h else o)

    def handle_register(self):
        fn = self.fullname.text().strip()
        code = self.staff_id.text().strip() 
        em = self.email.text().strip()
        pw = self.password.text().strip()
        cpw = self.password_confirm.text().strip()

        if not fn or not code or not em or not pw:
            QMessageBox.warning(self, "Lỗi", "Thiếu thông tin!"); return
        if pw != cpw:
            QMessageBox.warning(self, "Lỗi", "Mật khẩu không khớp!"); return
        
        role = "student" if self.rb_student.isChecked() else "teacher"

        suc, msg = register_user(
            fullname=fn, 
            user_code=code, 
            email=em, 
            username=code,  
            password=pw, 
            role=role       
        )

        if suc:
            QMessageBox.information(self, "Thành công", msg)
            self.btn_back.click()
        else:
            QMessageBox.warning(self, "Lỗi", msg)