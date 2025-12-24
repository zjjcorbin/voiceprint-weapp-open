from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.models.database import get_db
from app.models.employee import EmployeeModel
from app.core.security import get_current_user, get_admin_user
from app.models.user import UserModel

router = APIRouter()


@router.get("/")
async def get_employees(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取员工列表"""
    from sqlalchemy import select
    
    stmt = select(EmployeeModel).offset(skip).limit(limit)
    result = await db.execute(stmt)
    employees = result.scalars().all()
    
    return {"employees": employees, "total": len(employees)}


@router.get("/{employee_id}")
async def get_employee(
    employee_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """获取员工详情"""
    from sqlalchemy import select
    
    stmt = select(EmployeeModel).where(EmployeeModel.employee_id == employee_id)
    result = await db.execute(stmt)
    employee = result.scalar_one_or_none()
    
    if not employee:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="员工不存在"
        )
    
    return employee