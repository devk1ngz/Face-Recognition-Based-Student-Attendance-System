import os
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame, QGraphicsDropShadowEffect, QAction
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPixmap, QIcon
from app.controllers.auth_controller import authenticate_user
from app.config import STYLES_DIR, IMG_DIR

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cổng Thông Tin Điện Tử")
        self.setFixedSize(1000, 650)
        self.current_user_info = None
        self.user_role = None
        self.register_window = None
        
        self.set_window_icon()
        self.initUI()
        self.load_style()

    def set_window_icon(self):
        icon_path = os.path.join(IMG_DIR, "logo_humg.jpg")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))

    def load_style(self):
        style_path = os.path.join(STYLES_DIR, "login_style.qss")
        if os.path.exists(style_path):
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())

    def initUI(self):
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        self.login_card = QFrame()
        self.login_card.setObjectName("login_card")
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(25)
        shadow.setYOffset(8)
        shadow.setColor(QColor(0, 0, 0, 40))
        self.login_card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout()
        card_layout.setContentsMargins(50, 40, 50, 50)
        card_layout.setSpacing(15)
        self.login_card.setLayout(card_layout)

        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setFixedHeight(100)
        logo_path = os.path.join(IMG_DIR, "logo_humg.jpg")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            self.logo_label.setPixmap(pixmap.scaled(90, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.title = QLabel("ĐĂNG NHẬP HỆ THỐNG")
        self.title.setObjectName("title")
        self.title.setAlignment(Qt.AlignCenter)
        self.subtitle = QLabel("Vui lòng nhập thông tin tài khoản")
        self.subtitle.setObjectName("subtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Mã số sinh viên / Mã số giảng viên")
        self.username.setObjectName("input_user")
        self.username.setFixedHeight(45)

        self.password = QLineEdit()
        self.password.setPlaceholderText("Mật khẩu")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setObjectName("input_pass")
        self.password.setFixedHeight(45)
        
        self.setup_password_visibility()

        self.btn_login = QPushButton("ĐĂNG NHẬP")
        self.btn_login.setObjectName("btn_login")
        self.btn_login.setCursor(Qt.PointingHandCursor)
        self.btn_login.setFixedHeight(50)

        self.btn_register = QPushButton("Chưa có tài khoản? Đăng ký ngay")
        self.btn_register.setObjectName("btn_register")
        self.btn_register.setCursor(Qt.PointingHandCursor)

        card_layout.addWidget(self.logo_label)
        card_layout.addWidget(self.title)
        card_layout.addWidget(self.subtitle)
        card_layout.addSpacing(20)
        card_layout.addWidget(self.username)
        card_layout.addWidget(self.password)
        card_layout.addSpacing(10)
        card_layout.addWidget(self.btn_login)
        card_layout.addWidget(self.btn_register)

        main_layout.addStretch()
        main_layout.addWidget(self.login_card, alignment=Qt.AlignCenter)
        main_layout.addStretch()

        self.btn_register.clicked.connect(self.open_register)
        self.username.returnPressed.connect(self.btn_login.click)
        self.password.returnPressed.connect(self.btn_login.click)

    def setup_password_visibility(self):
        self.eye_open = QIcon(os.path.join(IMG_DIR, "eye.png"))
        self.eye_closed = QIcon(os.path.join(IMG_DIR, "eye_close.png"))
        self.toggle_action = self.password.addAction(self.eye_closed, QLineEdit.TrailingPosition)
        self.toggle_action.triggered.connect(self.toggle_password)
        self.is_pass_hidden = True

    def toggle_password(self):
        if self.is_pass_hidden:
            self.password.setEchoMode(QLineEdit.Normal)
            self.toggle_action.setIcon(self.eye_open)
            self.is_pass_hidden = False
        else:
            self.password.setEchoMode(QLineEdit.Password)
            self.toggle_action.setIcon(self.eye_closed)
            self.is_pass_hidden = True

    def open_register(self):
        if self.register_window is None:
            from app.ui.register import RegisterWindow
            self.register_window = RegisterWindow()
            self.register_window.btn_back.clicked.connect(self.back_to_login)
        self.register_window.show()
        self.hide()

    def back_to_login(self):
        self.register_window.hide()
        self.show()

    def validate_login(self):
        user_input = self.username.text().strip()
        pass_input = self.password.text().strip()
        if not user_input or not pass_input:
            QMessageBox.warning(self, "Lỗi", "Vui lòng nhập đầy đủ thông tin!")
            return False

        success, user_data = authenticate_user(user_input, pass_input)
        if success:
            self.user_role = user_data['role']
            self.current_user_info = user_data
            return True
        
        QMessageBox.warning(self, "Thất bại", "Sai tên đăng nhập hoặc mật khẩu!")
        return False