"""用户相关请求/响应模型"""

from typing import Optional
from pydantic import BaseModel, Field


class LoginUserVO(BaseModel):
    """登录用户视图对象"""

    id: int
    user_account: str = Field(..., alias="userAccount")
    user_name: Optional[str] = Field(None, alias="userName")
    user_avatar: Optional[str] = Field(None, alias="userAvatar")
    user_profile: Optional[str] = Field(None, alias="userProfile")
    user_role: str = Field(..., alias="userRole")
    create_time: str = Field(..., alias="createTime")
    update_time: str = Field(..., alias="updateTime")

    class Config:
        populate_by_name = True
