"""
题目API路由 - 第9步改造版
添加工作空间管理和冲突检测功能
优化：异步文件IO，防止阻塞事件循环
"""
import os
import io
import json
import shutil
import zipfile
import aiofiles
import asyncio
import logging
from datetime import datetime, date
from typing import cast
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form, Body, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from typing import List, Optional
from fastapi.responses import FileResponse
from app.crud import question as crud_question
from app.crud.upload import get_conflict_record, delete_upload_record, create_upload_record, delete_upload_record_by_batch_id
from app.schemas.question import (
    QuestionCreate, QuestionUpdate, QuestionResponse, StatisticsResponse,
    ConflictCheckRequest, QuestionBulkUpdateRequest
)
from app.models.upload_record import UploadRecord
from app.models.question import Question as QuestionModel
from app.core.database import get_db
from app.utils.folder_utils import (
    generate_batch_id, create_batch_folder, write_operations_json,
    get_batch_folder_path, get_all_operations_files, delete_batch_folder,
    remove_record_from_operations_json, read_operations_json
)
from app.services.quality_check import quality_check_batch, archive_waste, convert_image_urls

# 配置日志
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/questions", tags=["questions"])


@router.get("/statistics", response_model=StatisticsResponse)
async def get_statistics(
    db: AsyncSession = Depends(get_db)
):
    """
    获取统计数据
    
    返回总题数、各题型分布、标签统计
    """
    return await crud_question.get_statistics(db)


@router.get("/", response_model=List[dict])
async def get_questions(
    skip: int = Query(0, ge=0, description="跳过记录数"),
    limit: int = Query(100, ge=1, le=1000, description="返回记录数"),
    type: Optional[str] = Query(None, description="题目类型"),
    difficulty: Optional[str] = Query(None, description="难度"),
    status: Optional[str] = Query(None, description="状态"),
    subject: Optional[str] = Query(None, description="科目"),
    grade: Optional[int] = Query(None, description="年级"),
    education_level: Optional[str] = Query(None, description="学段"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取题目列表

    支持按类型、难度、状态、科目、年级、学段筛选
    返回驼峰命名格式
    """
    questions = await crud_question.get_questions(
        db, skip=skip, limit=limit, type=type, difficulty=difficulty, status=status,
        subject=subject, grade=grade, education_level=education_level
    )

    # 转换为驼峰命名
    def to_camel_case(q: QuestionModel) -> dict:
        return {
            "id": q.id,
            "questionNumber": q.question_number,
            "type": q.type,
            "difficulty": q.difficulty,
            "status": q.status,
            "stem": q.stem,
            "answer": q.answer,
            "options": json.loads(q.options) if q.options else [],
            "stemImages": json.loads(q.stem_images) if q.stem_images else [],
            "topics": json.loads(q.topics) if q.topics else [],
            "category": q.category,
            "analysis": q.analysis,
            "comment": q.comment,
            "statusMessage": q.status_message,
            "grade": q.grade,
            "subject": q.subject,
            "educationLevel": q.education_level,
            "source": q.source,
            "sourceFolder": q.source_folder,
            "version": q.version,
            "aiGrade": q.ai_grade,
            "aiDifficulty": q.ai_difficulty,
            "aiTopics": json.loads(q.ai_topics) if q.ai_topics else [],
            "aiCategory": q.ai_category,
            "aiAnalysis": q.ai_analysis,
            "aiReasoning": q.ai_reasoning,
            "aiModel": q.ai_model,
            "aiOptimizedAt": q.ai_optimized_at.isoformat() if q.ai_optimized_at else None,
            "isAiOptimized": bool(q.is_ai_optimized),
            "confirmedAt": q.confirmed_at.isoformat() if q.confirmed_at else None,
            "createdAt": q.created_at.isoformat() if q.created_at else None,
            "updatedAt": q.updated_at.isoformat() if q.updated_at else None,
        }

    return [to_camel_case(q) for q in questions]


@router.get("/upload-history")
async def get_upload_history(
    folder_code: str = Query(..., description="学科学段短代码，如：m7s9m2")
):
    """
    获取上传历史记录（从文件系统读取）

    读取 operations-*.json 文件，返回指定 folder_code 下的所有批次记录，
    按上传时间倒序排序。
    """
    try:
        # 获取所有 operations 文件
        operations_files = get_all_operations_files(folder_code)

        all_records = []
        education_level = ""
        subject = ""

        # 读取每个 operations 文件
        from datetime import datetime
        for file_path in operations_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                if not education_level and data.get("education_level"):
                    education_level = data["education_level"]
                if not subject and data.get("subject"):
                    subject = data["subject"]

                # 转换 records 格式
                for r in data.get("records", []):
                    all_records.append({
                        "batch_id": r.get("batch_id", ""),
                        "display_name": r.get("display_name", ""),
                        "timestamp": r.get("timestamp", ""),
                        "status": r.get("status", "completed"),
                        "teacher_name": r.get("teacher_name", ""),
                        "original_filename": r.get("original_filename", ""),
                        "file_count": r.get("file_count", 0),
                        "image_count": r.get("image_count", 0),
                    })
            except Exception as e:
                logger.warning(f"读取文件失败: {file_path}, error={e}")
                continue

        # 按时间倒序排序
        all_records.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        return {
            "folder_code": folder_code,
            "education_level": education_level,
            "subject": subject,
            "total_uploads": len(all_records),
            "records": all_records
        }

    except Exception as e:
        logger.error(f"获取历史记录失败: folder_code={folder_code}, error={e}", exc_info=True)
        return {
            "folder_code": folder_code,
            "education_level": "",
            "subject": "",
            "total_uploads": 0,
            "records": [],
            "error": str(e)
        }


@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    获取题目详情
    """
    question = await crud_question.get_question(db, question_id=question_id)
    if not question:
        raise HTTPException(
            status_code=404,
            detail=f"题目 {question_id} 不存在"
        )
    return question


@router.post("/", response_model=QuestionResponse, status_code=201)
async def create_question(
    question: QuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    创建题目
    """
    try:
        return await crud_question.create_question(db, question)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"创建题目失败: {str(e)}"
        )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: str,
    question: QuestionUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    更新题目
    """
    db_question = await crud_question.get_question(db, question_id)
    if not db_question:
        raise HTTPException(
            status_code=404,
            detail=f"题目 {question_id} 不存在"
        )

    try:
        return await crud_question.update_question(db, question_id, question)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"更新题目失败: {str(e)}"
        )


@router.delete("/{question_id}", status_code=204)
async def delete_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除题目
    """
    db_question = await crud_question.get_question(db, question_id)
    if not db_question:
        raise HTTPException(
            status_code=404,
            detail=f"题目 {question_id} 不存在"
        )

    await crud_question.delete_question(db, question_id=question_id)
    return None


@router.post("/check-conflict")
async def check_conflict(
    request: ConflictCheckRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    检查文件上传冲突

    检测同老师当天是否已上传同名文件
    """
    try:

        # 查询当天是否已有同名文件上传
        existing_record = await get_conflict_record(
            db, request.folder_code, request.teacher_name, request.original_filename, date.today()
        )
        
        if existing_record:
            # 发现冲突
            return {
                "conflict": True,
                "existing_record": {
                    "batch_id": existing_record.batch_id,
                    "display_name": existing_record.display_name,
                    "uploaded_at": existing_record.uploaded_at.isoformat(),
                    "file_count": existing_record.file_count or 0
                },
                "message": f"您今天已上传过'{request.original_filename}'，是否覆盖？",
                "options": ["覆盖", "重命名", "取消"]
            }
        else:
            # 无冲突
            return {
                "conflict": False,
                "message": "无冲突，可以上传",
                "options": ["覆盖", "重命名", "取消"]
            }
            
    except Exception as e:
        print(f"DEBUG: Conflict check failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"冲突检测失败: {str(e)}")


@router.post("/upload-folder")
async def upload_question_folder(
    json_file: UploadFile = File(..., description="题目 JSON 文件"),
    folder_name: str = Form(..., description="文件夹名称"),
    subject: str = Form(..., description="科目"),
    subject_code: str = Form(..., description="科目代码"),
    grade: str = Form(..., description="年级"),  # 改为 string，后端再转换
    education_level: str = Form(..., description="学段"),
    folder_code: str = Form(..., description="文件夹短代码"),
    teacher_name: str = Form(..., description="老师姓名"),
    conflict_action: str = Form(default="new", description="冲突处理方式"),
    db: AsyncSession = Depends(get_db)
):
    """
    上传试题文件夹（第 9 步改造版）
    
    业务逻辑下沉至 CRUD 层的重构入口，保持 API 签名不变。
    """
    from app.crud.upload import process_upload_folder
    return await process_upload_folder(
        db=db,
        json_file=json_file,
        folder_code=folder_code,
        folder_name=folder_name,
        subject=subject,
        education_level=education_level,
        grade=grade,
        teacher_name=teacher_name,
        conflict_action=conflict_action,
    )



@router.get("/batch/{batch_id}")
async def get_batch_questions(
    batch_id: str,
    folder_code: str = Query(..., description="学科学段短代码")
):
    """
    获取批次中的题目列表（从文件系统读取）

    从批次文件夹中读取 questions.json 文件，返回该批次的所有题目。
    """
    try:
        # 获取批次文件夹路径
        batch_path = get_batch_folder_path(folder_code, batch_id)
        questions_file = os.path.join(batch_path, "questions.json")

        if not os.path.exists(questions_file):
            raise HTTPException(
                status_code=404,
                detail=f"批次 {batch_id} 不存在"
            )

        # 读取 questions.json
        with open(questions_file, 'r', encoding='utf-8') as f:
            questions_data = json.load(f)

        questions = questions_data.get("questions", [])
        error_count = sum(1 for q in questions if q.get("status") in ("error", "waste"))

        return {
            "batch_id": batch_id,
            "folder_code": folder_code,
            "display_name": questions_data.get("display_name", batch_id),
            "questions": questions,
            "total": len(questions),
            "error_count": error_count,
            "valid_count": len(questions) - error_count
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取批次题目失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取批次题目失败: {str(e)}")


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
        print(f"DEBUG: Get batch image failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"获取图片失败: {str(e)}")



@router.post("/batch/{batch_id}/bulk-update", response_model=dict)
async def bulk_update_questions(
    batch_id: str,
    request: QuestionBulkUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    批量更新批次中的题目

    用于保存脚本预处理的结果或批量修改
    直接修改文件系统中的JSON文件
    """
    if batch_id != request.batch_id:
        raise HTTPException(status_code=400, detail="路径中的batch_id与请求体不一致")

    try:
        # 1. 查询批次记录
        result = await db.execute(
            select(UploadRecord).where(UploadRecord.batch_id == batch_id)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise HTTPException(status_code=404, detail=f"批次 {batch_id} 不存在")

        # 2. 确定内容目录
        content_dir = cast(str, record.full_path)
        if not os.path.exists(content_dir):
            raise HTTPException(status_code=404, detail=f"批次目录不存在")

        file_list = os.listdir(content_dir)
        if len(file_list) == 1 and os.path.isdir(os.path.join(content_dir, file_list[0])):
            content_dir = os.path.join(content_dir, file_list[0])

        # 3. 获取所有JSON文件（必须排序以保证ID一致性）
        json_files = sorted([f for f in os.listdir(content_dir) if f.endswith('.json')])

        # 建立更新映射: ID -> UpdateItem
        update_map = {q.id: q for q in request.questions}
        updated_count = 0
        total_processed = 0

        # 4. 逐个文件处理
        for json_filename in json_files:
            file_path = os.path.join(content_dir, json_filename)
            file_changed = False

            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)

            if not isinstance(data, list):
                continue

            # 处理文件中的每个题目
            for question in data:
                # 重新计算ID以匹配
                current_id = question.get("id")
                if not current_id:
                    current_id = f"{batch_id}-Q{total_processed + 1:03d}"

                # 检查是否需要更新
                if current_id in update_map:
                    update_item = update_map[current_id]
                    updates = update_item.model_dump(exclude_unset=True, exclude={'id'})

                    if updates:
                        # 确保ID被持久化
                        if "id" not in question:
                            question["id"] = current_id

                        # 应用更新
                        question.update(updates)
                        file_changed = True
                        updated_count += 1

                total_processed += 1

            # 如果文件有变更，写回磁盘
            if file_changed:
                async with aiofiles.open(file_path, 'w', encoding='utf-8') as f:
                    await f.write(json.dumps(data, ensure_ascii=False, indent=2))

        return {
            "success": True,
            "updated_count": updated_count,
            "message": f"成功更新 {updated_count} 条题目数据"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"批量更新失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"批量更新失败: {str(e)}")


async def delete_batch(
    batch_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    删除批次记录

    删除指定批次的所有数据：
    1. 删除批次文件夹
    2. 从 operations.json 删除记录
    3. 删除数据库记录

    注意：此操作不会删除已入库的题目，只删除批次记录和文件夹
    """
    try:
        # 1. 查询批次记录，获取 folder_code
        result = await db.execute(
            select(UploadRecord).where(UploadRecord.batch_id == batch_id)
        )
        record = result.scalar_one_or_none()

        if not record:
            raise HTTPException(
                status_code=404,
                detail=f"批次 {batch_id} 不存在"
            )

        folder_code = cast(str, record.folder_code)

        # 2. 删除批次文件夹
        delete_batch_folder(folder_code, batch_id)

        # 3. 从 operations.json 删除记录
        remove_record_from_operations_json(folder_code, batch_id)

        # 4. 删除数据库记录
        await delete_upload_record_by_batch_id(db, batch_id)

        return None

    except HTTPException:
        raise
    except Exception as e:
        print(f"DEBUG: Delete batch failed: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"删除批次失败: {str(e)}")
