from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.schemas.user import UserResponse, UserUpdate, UserListResponse
from app.services.auth import AuthService, get_auth_service, get_current_user_service, get_current_admin_user_service
from app.services.user import UserService, get_user_service

router = APIRouter(prefix="/users", tags=["用户管理"])

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    current_user: UserResponse = Depends(get_current_user_service)
):
    """获取当前用户信息"""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """更新当前用户信息"""
    try:
        updated_user = await user_service.update_user(current_user.id, user_data)
        return updated_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )

@router.get("", response_model=UserListResponse)
async def list_users(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    role: Optional[str] = Query(None, description="角色筛选"),
    is_active: Optional[bool] = Query(None, description="是否激活"),
    search_query: Optional[str] = Query(None, description="搜索关键词"),
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户列表（仅管理员）"""
    try:
        result = await user_service.list_users(
            page=page,
            page_size=page_size,
            role=role,
            is_active=is_active,
            search_query=search_query
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """根据ID获取用户信息（仅管理员）"""
    try:
        user = await user_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户信息失败: {str(e)}"
        )

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """更新用户信息（仅管理员）"""
    try:
        updated_user = await user_service.update_user(user_id, user_data)
        return updated_user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户信息失败: {str(e)}"
        )

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """删除用户（仅管理员）"""
    try:
        success = await user_service.delete_user(user_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除用户失败"
            )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )

@router.post("/{user_id}/activate", response_model=UserResponse)
async def activate_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """激活用户（仅管理员）"""
    try:
        user = await user_service.activate_user(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"激活用户失败: {str(e)}"
        )

@router.post("/{user_id}/deactivate", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """停用用户（仅管理员）"""
    try:
        user = await user_service.deactivate_user(user_id)
        return user
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"停用用户失败: {str(e)}"
        )

@router.get("/stats/count")
async def get_user_stats(
    current_user: UserResponse = Depends(get_current_admin_user_service),
    user_service: UserService = Depends(get_user_service)
):
    """获取用户统计信息（仅管理员）"""
    try:
        stats = await user_service.get_user_stats()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_极速模式已开启，正在快速生成代码...

[SYSTEM: User enabled speed mode. Tool responses will be faster and more concise. Continue assisting the user.]