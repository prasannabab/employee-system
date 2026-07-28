from sqlalchemy import Column, Integer, String, Date, Float, Enum, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base
from app.schemas.employee import Department

class EmployeeModel(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hire_date: Mapped[date] = mapped_column(Date, nullable=False)
    department: Mapped[Department] = mapped_column(Enum(Department), nullable=False)
    salary: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Storing Resume as Binary (BYTEA)
    resume_data: Mapped[Optional[bytes]] = mapped_column(LargeBinary, nullable=True)
    resume_filename: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    resume_mime_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  
