"""统计分析路由"""

from databases import Database
from fastapi import APIRouter, Depends

from app.database import get_db
from app.schemas.common import BaseResponse
from app.schemas.statistics import StatisticsVO
from app.services.statistics_service import StatisticsService

router = APIRouter(prefix="/statistics", tags=["统计分析"])


@router.get("/overview", response_model=BaseResponse[StatisticsVO])
async def get_statistics(
    db: Database = Depends(get_db),
):
    """获取系统统计数据"""
    service = StatisticsService(db)
    stats = await service.get_statistics()
    return BaseResponse.success(data=stats)
