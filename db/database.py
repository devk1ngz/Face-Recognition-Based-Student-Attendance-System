from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_db"]

users_col = db["users"]
students_col = db["students"]
classes_col = db["classes"]
attendance_col = db["attendance"]

# === Users ===
def get_user(username, password):
    return users_col.find_one({"username": username, "password": password})

# === Students ===
def insert_student(student_id, name, class_id, embedding):
    students_col.insert_one({
        "student_id": student_id,
        "name": name,
        "class_id": class_id,
        "embedding": embedding.tolist()
    })

def get_students_by_class(class_id):
    return list(students_col.find({"class_id": class_id}))

# === Attendance ===
def insert_attendance(student_id, class_id, status):
    attendance_col.insert_one({
        "student_id": student_id,
        "class_id": class_id,
        "status": status
    })
