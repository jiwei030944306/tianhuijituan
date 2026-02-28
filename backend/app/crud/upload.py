"""
上传相关的CRUD操作
"""
from __future__ import annotations

import io
import json
import os
import shutil
import zipfile
from datetime import datetime, date
from typing import Optional

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi import UploadFile, HTTPException, status
from app.models.upload_record import UploadRecord
from app.utils.folder_utils import (
    generate_batch_id, create_batch_folder, write_operations_json,
    get_batch_folder_path, get_all_operations_files, delete_batch_folder, remove_record_from_operations_json
)
from app.services.quality_check import quality_check_batch, archive_waste, convert_image_urls
from app.services.question_validation import validate_questions_batch, format_validation_report

logger = __import__("logging").getLogger(__name__)

async def process_upload_folder(
    db: AsyncSession,
    json_file: UploadFile,
    folder_code: str,
    folder_name: str,
    subject: str,
    education_level: str,
    grade: Optional[str] = None,  # 改为 str，因为前端可能发 "8" 或 "11"
    teacher_name: str = "",
    conflict_action: str = "new",
) -> dict:
    """Process uploading a question folder. Heavy business logic moved from API route.

    This function encapsulates the original upload-question-folder workflow:
    - optional overwrite handling via existing upload records
    - batch folder creation and ZIP extraction/validation
    - JSON parsing to count questions and detect types
    - image counting
    - DB record creation and operations.json update
    - quality check and AI URL conversion
    - return a consistent response payload identical to the API route
    """
    try:
        # 1. Overwrite handling: delete old records if requested
        if conflict_action == "overwrite":
            filename = json_file.filename or "unknown.zip"
            await delete_upload_record(
                db, folder_code, teacher_name, filename, date.today()
            )

        # 2. Batch and folder setup
        batch_id = generate_batch_id()
        record_date = date.today()
        batch_folder = create_batch_folder(folder_code, batch_id)
        json_path = os.path.join(batch_folder, "questions.json")
        image_count = 0
        question_count = 0

        # 初始化题型统计（与前端定义保持一致）
        type_stats = {
            "single_choice": 0,
            "multiple_choice": 0,
            "basic_fill": 0,
            "calculation": 0,
            "application": 0,
            "subjective": 0
        }

        # 3. Read ZIP content
        zip_content = await json_file.read()

        # 4. Unzip safely
        try:
            with zipfile.ZipFile(io.BytesIO(zip_content), 'r') as zip_ref:
                # security: reject dangerous paths
                for member in zip_ref.namelist():
                    if member.startswith('/') or '..' in member or member.startswith('\\'):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"安全警告：ZIP文件包含不安全的路径：{member}"
                        )
                zip_ref.extractall(batch_folder)

                content_dir = batch_folder
                file_list = os.listdir(batch_folder)
                if len(file_list) == 1 and os.path.isdir(os.path.join(batch_folder, file_list[0])):
                    content_dir = os.path.join(batch_folder, file_list[0])
                    file_list = os.listdir(content_dir)
                # 先初始化计数器和 JSON 文件列表
                image_count = 0
                question_count = 0
                json_files = [f for f in file_list if f.endswith('.json')]

                # 解析 JSON 文件
                for json_filename in json_files:
                    try:
                        with open(os.path.join(content_dir, json_filename), 'r', encoding='utf-8') as f:
                            questions_data = json.load(f)
                            if isinstance(questions_data, list):
                                question_count += len(questions_data)
                                
                                # 验证题目数据
                                validation_result = validate_questions_batch(questions_data)
                                if validation_result["invalid"] > 0:
                                    logger.warning(
                                        f"JSON 文件 {json_filename} 中有 {validation_result['invalid']} 道无效题目:\n"
                                        f"{format_validation_report(validation_result)}"
                                    )
                                
                                # 统计题型
                                for question in questions_data:
                                    q_type = question.get("type", "unknown")
                                    if q_type in type_stats:
                                        type_stats[q_type] += 1
                    except Exception as e:
                        print(f"警告：无法解析 JSON 文件 {json_filename}: {e}")

                # 统计图片数量
                images_dir = os.path.join(content_dir, 'images')
                if os.path.exists(images_dir) and os.path.isdir(images_dir):
                    image_files = [f for f in os.listdir(images_dir)
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
                    image_count = len(image_files)
        except zipfile.BadZipFile:
            # If not a zip, treat content as raw JSON
            with open(json_path, 'wb') as f:
                f.write(zip_content)
            try:
                questions_data = json.loads(zip_content.decode('utf-8'))
                if isinstance(questions_data, list):
                    question_count = len(questions_data)
                    
                    # 验证题目数据
                    validation_result = validate_questions_batch(questions_data)
                    if validation_result["invalid"] > 0:
                        logger.warning(
                            f"上传的 JSON 数据中有 {validation_result['invalid']} 道无效题目:\n"
                            f"{format_validation_report(validation_result)}"
                        )
                    
                    # 统计题型
                    for question in questions_data:
                        q_type = question.get("type", "unknown")
                        if q_type in type_stats:
                            type_stats[q_type] += 1
                
                # 统计图片数量
                images_dir = os.path.join(batch_folder, 'images')
                if os.path.exists(images_dir) and os.path.isdir(images_dir):
                    image_files = [f for f in os.listdir(images_dir)
                                   if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp'))]
                    image_count = len(image_files)
            except Exception:
                pass

        # 5. DB record creation
        filename = json_file.filename or "unknown.zip"
        record = await create_upload_record(
            db=db,
            folder_code=folder_code,
            education_level=education_level,
            subject=subject,
            batch_id=batch_id,
            record_date=record_date,
            full_path=batch_folder,
            display_name=folder_name,
            original_filename=filename,
            teacher_name=teacher_name,
            file_count=question_count,
            image_count=image_count,
            status="completed",
        )

        # 6. Update operations.json
        dominant_type = "unknown"
        if any(type_stats.values()):
            dominant_type = max(type_stats.keys(), key=lambda k: type_stats[k])

        operations_record = {
            "batch_id": batch_id,
            "timestamp": datetime.now().isoformat(),
            "teacher_name": teacher_name,
            "display_name": folder_name,
            "original_filename": json_file.filename,
            "file_count": question_count,
            "image_count": image_count,
            "status": "completed",
            "type_distribution": type_stats,
            "dominant_type": dominant_type,
        }
        write_operations_json(folder_code, education_level, subject, record_date, operations_record)

        # 7. Return result payload identical to API route
        return {
            "success": True,
            "batch_id": batch_id,
            "folder_code": folder_code,
            "record_date": record_date.strftime("%Y-%m-%d"),
            "full_path": batch_folder,
            "display_name": folder_name,
            "question_count": question_count,
            "image_count": image_count,
            "uploaded_at": record.uploaded_at.isoformat(),
            "operations_file": f"operations-{record_date.strftime('%Y%m%d')}.json",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"上传失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(e)}")

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, delete
from datetime import date
from typing import Optional
from app.models.upload_record import UploadRecord


async def get_conflict_record(
    db: AsyncSession,
    folder_code: str,
    teacher_name: str,
    original_filename: str,
    record_date: date
) -> Optional[UploadRecord]:
    """
    查询冲突记录
    
    检查同老师当天是否已上传同名文件
    """
    query = select(UploadRecord).where(
        and_(
            UploadRecord.folder_code == folder_code,
            UploadRecord.teacher_name == teacher_name,
            UploadRecord.record_date == record_date,
            UploadRecord.original_filename == original_filename
        )
    )
    
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def delete_upload_record(
    db: AsyncSession,
    folder_code: str,
    teacher_name: str,
    original_filename: str,
    record_date: date
) -> bool:
    """
    删除上传记录（用于覆盖模式）

    Returns:
        是否成功删除
    """
    query = delete(UploadRecord).where(
        and_(
            UploadRecord.folder_code == folder_code,
            UploadRecord.teacher_name == teacher_name,
            UploadRecord.record_date == record_date,
            UploadRecord.original_filename == original_filename
        )
    )

    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0  # type: ignore


async def create_upload_record(
    db: AsyncSession,
    folder_code: str,
    education_level: str,
    subject: str,
    batch_id: str,
    record_date: date,
    full_path: str,
    display_name: str,
    original_filename: str,
    teacher_name: str,
    file_size: Optional[int] = None,
    file_count: Optional[int] = None,
    image_count: Optional[int] = None,
    status: str = "completed"
) -> UploadRecord:
    """
    创建上传记录
    """
    record = UploadRecord(
        folder_code=folder_code,
        education_level=education_level,
        subject=subject,
        batch_id=batch_id,
        record_date=record_date,
        full_path=full_path,
        display_name=display_name,
        original_filename=original_filename,
        teacher_name=teacher_name,
        file_size=file_size,
        file_count=file_count,
        image_count=image_count,
        status=status
    )

    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


async def delete_upload_record_by_batch_id(
    db: AsyncSession,
    batch_id: str
) -> bool:
    """
    按 batch_id 删除上传记录

    Args:
        db: 数据库会话
        batch_id: 批次ID

    Returns:
        是否成功删除
    """
    query = delete(UploadRecord).where(UploadRecord.batch_id == batch_id)

    result = await db.execute(query)
    await db.commit()
    return result.rowcount > 0  # type: ignore
