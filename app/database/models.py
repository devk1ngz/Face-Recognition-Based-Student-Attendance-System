from sqlalchemy import Column, Integer, String, ForeignKey, LargeBinary, Boolean, Date
from sqlalchemy.orm import relationship
from app.database.connector import Base
import datetime

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    fullname = Column(String)
    user_code = Column(String)
    email = Column(String)
    role = Column(String) 
    phone_number = Column(String, nullable=True) 
    avatar = Column(String, nullable=True)       
    courses = relationship("Course", back_populates="teacher")
    student_profile = relationship("Student", back_populates="user_account", uselist=False)

class Course(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True)
    course_code = Column(String, unique=True)
    course_name = Column(String)
    credits = Column(Integer, default=3) 
    teacher_id = Column(Integer, ForeignKey('users.id'))
    teacher = relationship("User", back_populates="courses")
    students = relationship("Student", back_populates="course")

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    mssv = Column(String, unique=True)
    name = Column(String)
    dob = Column(Date, nullable=True)       
    class_name = Column(String, nullable=True)
    avatar = Column(String, nullable=True) 
    email = Column(String, nullable=True)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship("Course", back_populates="students")
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    user_account = relationship("User", back_populates="student_profile")
    face_encoding = Column(LargeBinary, nullable=True) 
    has_face = Column(Boolean, default=False)
    attendances = relationship("Attendance", back_populates="student")

class Attendance(Base):
    __tablename__ = 'attendances'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    date = Column(String)
    time = Column(String)
    status = Column(String)
    note = Column(String, nullable=True)
    student = relationship("Student", back_populates="attendances")