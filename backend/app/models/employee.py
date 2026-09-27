from sqlalchemy import Column, String, Boolean
from app.db.session import Base


class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String(20), primary_key=True)
    full_name = Column(String(100), nullable=False)
    role = Column(String(50), nullable=False)  # e.g. STAFF, MANAGER, ENGINEERING
    department = Column(String(50), nullable=False)
    email = Column(String(100), unique=True)
    auth_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
