from pydantic import BaseModel, Field, field_validator, model_validator, computed_field, ConfigDict, EmailStr, HttpUrl, constr
from typing import Optional, List, Annotated
from datetime import datetime, date
from enum import Enum

class Department(str, Enum):
    ENGINEERING = "engineering"
    HR = "hr"
    SALES = "sales"

# Custom Annotated Type for strict string handling
NonEmptyStr = Annotated[str, Field(min_length=1, strip_whitespace=True)]

class EmployeeCreate(BaseModel):
    full_name: NonEmptyStr
    email: EmailStr
    hire_date: date = Field(default_factory=datetime.now().date, description="Date of joining")
    department: Department
    salary: float = Field(ge=0, description="Annual salary")
    
    # Field Validator: Custom logic for specific field
    @field_validator('full_name')
    @classmethod
    def validate_name_caps(cls, v):
        if not v[0].isupper():
            raise ValueError('Full name must start with a capital letter')
        return v.title()

    # Model Validator: Cross-field validation
    @model_validator(mode='after')
    def check_hire_date_logic(self):
        if self.hire_date > datetime.now().date():
            raise ValueError('Hire date cannot be in the future')
        return self

class EmployeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, json_schema_extra={"example": {"id": 1}})
    
    id: int
    full_name: str
    email: str
    department: Department
    hire_date: date
    years_of_service: int
    
    # Computed Field: Dynamic value not stored in DB
    @computed_field
    @property
    def years_of_service(self) -> int:
        return datetime.now().year - self.hire_date.year

    class Config:
        populate_by_name = True   
