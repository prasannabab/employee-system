from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, Query, Path
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db.session import get_db
from app.commands.employee_commands import EmployeeCommands
from app.queries.employee_queries import EmployeeQueries
from app.schemas.employee import EmployeeCreate, EmployeeResponse
from app.core.security import get_current_user
import io

router = APIRouter(prefix="/employees", tags=["Employees"])

# Background Task Simulation
def process_resume_analysis(emp_id: int, file_size: int):
    # Simulate heavy CPU task like OCR or Virus Scan
    print(f"Background: Analyzing resume for emp {emp_id}, size: {file_size}")

@router.post("/", response_model=EmployeeResponse, status_code=201)
async def create_employee(
    employee: EmployeeCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user) # Auth at API level
):
    new_emp = await EmployeeCommands.create_employee(db, employee)
    return new_emp

@router.post("/{emp_id}/resume")
async def upload_resume(
    emp_id: int = Path(..., gt=0, description="Employee ID"),
    file: UploadFile = File(..., description="Resume PDF/DOCX"),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    current_user: dict = Depends(get_current_user)
):
    # Validate file type
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(400, "Only PDF or DOCX allowed")
    
    content = await file.read()
    
    await EmployeeCommands.upload_resume(db, emp_id, content, file.filename, file.content_type)
    
    # Add background task to process the file AFTER response is sent
    background_tasks.add_task(process_resume_analysis, emp_id, len(content))
    
    return {"message": "Resume uploaded successfully", "filename": file.filename}

@router.get("/{emp_id}/resume/download")
async def download_resume(
    emp_id: int = Path(...),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    emp = await EmployeeQueries.get_employee_by_id(db, emp_id)
    if not emp or not emp.resume_data:
        raise HTTPException(404, "Resume not found")
    
    # Stream the binary data from DB
    stream = io.BytesIO(emp.resume_data)
    return StreamingResponse(
        stream, 
        media_type=emp.resume_mime_type,
        headers={"Content-Disposition": f"attachment; filename={emp.resume_filename}"}
    )

@router.get("/", response_model=List[EmployeeResponse])
async def list_employees(
    skip: int = Query(0, ge=0, description="Number to skip"),
    limit: int = Query(10, ge=1, le=100, description="Max results"),
    dept: Optional[str] = Query(None, description="Filter by department"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    # Simple query logic expansion could go here
    employees = await EmployeeQueries.get_all_employees(db, skip, limit)
    return employees  
