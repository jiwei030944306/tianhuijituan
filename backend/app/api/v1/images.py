"""
图片服务API路由

提供图片文件访问接口
"""
import os
from typing import cast

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.upload_record import UploadRecord

router = APIRouter()


@router.get("/batch/{batch_id}/image/{image_name}")
async def get_batch_image(
    batch_id: str,
    image_name: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取批次中的图片

    返回指定批次中的图片文件
    """
    try:
        # 1. 查询批次记录，获取 full_path
        result = await db.execute(
            select(UploadRecord).where(UploadRecord.batch_id == batch_id)
        )
        record = result.scalar_one_or_none()


        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"批次 {batch_id} 不存在"
            )

        # 2. 确定内容目录
        content_dir = cast(str, record.full_path)
        file_list = os.listdir(content_dir)

        # 如果只有一个子目录，使用该子目录
        if len(file_list) == 1 and os.path.isdir(os.path.join(content_dir, file_list[0])):
            content_dir = os.path.join(content_dir, file_list[0])

        # 3. 构建图片路径
        image_path = os.path.join(content_dir, 'images', image_name)

        # 4. 检查图片是否存在
        if not os.path.exists(image_path):
            raise HTTPException(
                status_code=404,
                detail=f"图片 {image_name} 不存在"
            )

        # 5. 返回图片文件
        return FileResponse(
            image_path,
            media_type="image/jpeg"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")
