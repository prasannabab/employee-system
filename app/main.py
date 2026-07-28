from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.employees import router as employee_router
from app.core.middleware import CustomHeaderMiddleware
from app.db.session import engine
from app.db.models import Base

app = FastAPI(title="Employee CQRS System", version="1.0.0")

# Middleware Order Matters
app.add_middleware(CustomHeaderMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employee_router, prefix="/api/v1")

@app.on_event("startup")
async def on_startup():
    # Create tables (Use Alembic in production)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  
