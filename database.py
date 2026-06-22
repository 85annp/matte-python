from sqlalchemy import create_engine, Column, String, Integer, Text, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
import uuid
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'matte_python.db')}")

if SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    saved_codes = relationship("SavedCode", back_populates="user")


class Lesson(Base):
    __tablename__ = "lessons"
    id = Column(Integer, primary_key=True, index=True)
    lesson_number = Column(Integer, nullable=False, unique=True, index=True)
    title = Column(String, index=True)
    theory_content = Column(Text)
    tasks = relationship("Task", back_populates="lesson")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    lesson_id = Column(Integer, ForeignKey("lessons.id"))
    task_number = Column(Integer, nullable=False, default=1)
    level = Column(Integer)  # 1 or 2
    prompt = Column(Text)
    default_code = Column(Text)
    expected_output = Column(Text, nullable=True)  # Optional, can be used later

    lesson = relationship("Lesson", back_populates="tasks")


class SavedCode(Base):
    __tablename__ = "saved_codes"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), primary_key=True)
    code = Column(Text)

    user = relationship("User", back_populates="saved_codes")


class Activity(Base):
    __tablename__ = "activities"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    default_code = Column(Text)
    questions = relationship("ActivityQuestion", back_populates="activity")


class ActivityQuestion(Base):
    __tablename__ = "activity_questions"
    id = Column(Integer, primary_key=True, index=True)
    activity_id = Column(Integer, ForeignKey("activities.id"))
    prompt = Column(Text)
    correct_answer = Column(String)  # We can store as string and parse on grading
    
    activity = relationship("Activity", back_populates="questions")


class ActivitySavedCode(Base):
    __tablename__ = "activity_saved_codes"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    activity_id = Column(Integer, ForeignKey("activities.id"), primary_key=True)
    code = Column(Text)


class ActivityAnswer(Base):
    __tablename__ = "activity_answers"
    user_id = Column(String, ForeignKey("users.id"), primary_key=True)
    question_id = Column(Integer, ForeignKey("activity_questions.id"), primary_key=True)
    answer = Column(String)

def _needs_rebuild() -> bool:
    db_path = os.path.join(BASE_DIR, "matte_python.db")
    if not os.path.exists(db_path):
        return True

    with engine.connect() as conn:
        task_columns = conn.exec_driver_sql("PRAGMA table_info(tasks)").fetchall()
        lesson_columns = conn.exec_driver_sql("PRAGMA table_info(lessons)").fetchall()
        activity_columns = conn.exec_driver_sql("PRAGMA table_info(activities)").fetchall()
        if not task_columns or not lesson_columns or not activity_columns:
            return True
        task_needs = any(column[1] == "task_number" for column in task_columns) is False
        lesson_needs = any(column[1] == "lesson_number" for column in lesson_columns) is False
        return task_needs or lesson_needs


def init_db():
    if _needs_rebuild():
        Base.metadata.drop_all(bind=engine)

    Base.metadata.create_all(bind=engine)
