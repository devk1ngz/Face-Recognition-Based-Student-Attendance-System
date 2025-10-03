from db.database import get_user

sessions = {}

def login(username, password):
    user = get_user(username, password)
    if user:
        sessions[username] = user  # lưu session
        return True, user
    return False, None

def get_session(username):
    return sessions.get(username, None)

def logout(username):
    if username in sessions:
        del sessions[username]
