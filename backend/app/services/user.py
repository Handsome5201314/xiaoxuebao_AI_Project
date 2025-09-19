from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, desc, and_, or_, text
from typing import List, Optional, Dict, Any
from fastapi import HTTPException, status, Depends

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserUpdate, UserListResponse
from app.services.auth import get_current_user_service

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        result = await self.db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def update_user(self, user_id: int, user_data: UserUpdate) -> User:
        """更新用户信息"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        update_dict = user_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(user, field, value)
        
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def list_users(
        self,
        page: int = 1,
        page_size: int = 20,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
        search_query: Optional[str] = None
    ) -> UserListResponse:
        """获取用户列表"""
        query = select(User)
        
        # 添加过滤条件
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        if search_query:
            query = query.where(
                or_(
                    User.email.ilike(f"%{search_query}%"),
                    User.display_name.ilike(f"%{search_query}%")
                )
            )
        
        # 计算总数
        count_query = select(func.count()).select_from(query.subquery())
        total_count = (await self.db.execute(count_query)).scalar()
        
        # 分页和排序
        query = query.order_by(desc(User.created_at))
        query = query.offset((page - 1) * page_size).limit(page_size)
        
        result = await self.db.execute(query)
        users = result.scalars().all()
        
        return UserListResponse(
            users=users,
            total_count=total_count,
            page=page,
            page_size=page_size,
            total_pages=(total_count + page_size - 1) // page_size
        )
    
    async def delete_user(self, user_id: int) -> bool:
        """删除用户（软删除）"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.is_active = False
        user.is_deleted = True
        await self.db.commit()
        return True
    
    async def activate_user(self, user_id: int) -> User:
        """激活用户"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.is_active = True
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def deactivate_user(self, user_id: int) -> User:
        """停用用户"""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        user.is_active = False
        await self.db.commit()
        await self.db.refresh(user)
        return user
    
    async def get_user_stats(self) -> Dict[str, Any]:
        """获取用户统计信息"""
        total_users = await self.db.scalar(select(func.count(User.id)))
        active_users = await self.db.scalar(
            select(func.count(User.id)).where(User.is_active == True)
        )
        admin_users = await self.db.scalar(
            select(func.count(User.id)).where(User.role == "admin")
        )
        
        # 最近注册统计
        recent_users = await self.db.scalar(
            select(func.count(User.id)).where(
                User.created_at >= func.now() - func.text("interval '7 days'")
            )
        )
        
        return {
            "total_users": total_users or 0,
            "active_users": active_users or 0,
            "admin_users": admin_users or 0,
            "recent_registrations": recent_users or 0
        }

# 依赖注入函数
async def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """获取用户服务实例"""
    return UserService(db)