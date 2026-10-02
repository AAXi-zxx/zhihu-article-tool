"""用户路由"""

from fastapi import APIRouter, Depends

from app.schemas.common import BaseResponse
from app.schemas.user import LoginUserVO
from app.deps import require_login

router = APIRouter(prefix="/user", tags=["用户"])


@router.get("/get/login", response_model=BaseResponse[LoginUserVO])
async def get_login_user(
    current_user: LoginUserVO = Depends(require_login)
):
    """获取当前用户身份（取消登录后固定返回游客用户）"""
    return BaseResponse.success(data=current_user)
