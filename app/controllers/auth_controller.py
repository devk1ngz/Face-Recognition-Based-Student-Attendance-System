from app.database.connector import get_session
from app.database.models import User

def authenticate_user(username, password):
    session = get_session()
    try:
        user = session.query(User).filter_by(username=username, password=password).first()
        if user:
            user_data = {
                "id": user.id,
                "fullname": user.fullname,
                "code": user.user_code,
                "role": user.role
            }
            return True, user_data
        else:
            return False, None
    finally:
        session.close()

def register_user(fullname, user_code, email, username, password, role="teacher"):
    session = get_session()
    try:
        if session.query(User).filter_by(username=username).first():
            return False, "Tên đăng nhập đã tồn tại!"

        new_user = User(fullname=fullname, user_code=user_code, email=email, username=username, password=password, role=role)
        session.add(new_user)
        session.commit()
        return True, "Đăng ký thành công!"
    except Exception as e:
        return False, str(e)
    finally:
        session.close()