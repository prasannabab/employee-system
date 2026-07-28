from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import EmployeeModel
from app.schemas.employee import EmployeeCreate

class EmployeeCommands:
    @staticmethod
    async def create_employee(db: AsyncSession, data: EmployeeCreate) -> EmployeeModel:
        new_emp = EmployeeModel(**data.model_dump())
        db.add(new_emp)
        await db.flush() # Get ID before commit
        await db.refresh(new_emp)
        return new_emp

    @staticmethod
    async def upload_resume(db: AsyncSession, emp_id: int, file_content: bytes, filename: str, mime_type: str):
        stmt = select(EmployeeModel).where(EmployeeModel.id == emp_id)
        result = await db.execute(stmt)
        emp = result.scalar_one_or_none()
        if not emp:
            raise ValueError("Employee not found")
        
        emp.resume_data = file_content
        emp.resume_filename = filename
        emp.resume_mime_type = mime_type
        # No commit here, handled by dependency

# app/queries/employee_queries.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.sql import func
from app.db.models import EmployeeModel

class EmployeeQueries:
    @staticmethod
    async def get_all_employees(db: AsyncSession, skip: int, limit: int):
        stmt = select(EmployeeModel).offset(skip).limit(limit)
        result = await db.execute(stmt)
        return result.scalars().all()

    @staticmethod
    async def get_employee_by_id(db: AsyncSession, emp_id: int):
        stmt = select(EmployeeModel).where(EmployeeModel.id == emp_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()   
