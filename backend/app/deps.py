"""依赖注入"""

import uuid
from typing import Optional
from fastapi import Cookie, Depends, HTTPException, status

from app.exceptions import ErrorCode, BusinessException
from app.schemas.user import LoginUserVO
from app.utils.session import get_session


async def get_session_id(session_id: Optional[str] = Cookie(None, alias="SESSION")) -> Optional[str]:
    """从 Cookie 中获取 Session ID"""
    return session_id


async def get_current_user(
    session_id: Optional[str] = Depends(get_session_id)
) -> Optional[LoginUserVO]:
    if not session_id:
        return None
    
    session_data = await get_session(session_id)
    if not session_data or "user" not in session_data:
        return None
    
    user_data = session_data["user"]
    return LoginUserVO(**user_data)

GUEST_USER = LoginUserVO(
    id=1,
    user_account="guest",
    user_name="游客",
    user_role="admin",
    create_time="2026-01-01 00:00:00",
    update_time="2026-01-01 00:00:00",
)


async def require_login(
    current_user: Optional[LoginUserVO] = Depends(get_current_user)
) -> LoginUserVO:
    if not current_user:
        return GUEST_USER
    return current_user


async def require_admin(
    current_user: LoginUserVO = Depends(require_login)
) -> LoginUserVO:
    if current_user.user_role != "admin":
        raise BusinessException(ErrorCode.NO_AUTH_ERROR)
    return current_user


def generate_session_id() -> str:
    """生成 Session ID"""
    return str(uuid.uuid4())
