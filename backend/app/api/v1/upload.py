from __future__ import annotations

import asyncio
from datetime import datetime
from pathlib import Path
import uuid
from typing import List, Optional

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/upload", tags=["upload"])

# --------------- 内部简单状态存储 ---------------
# 实践中应将任务状态落入持久存储，如数据库或缓存，本示例使用内存以降低实现复杂度。
class _UploadTask(BaseModel):
    id: str
    filename: str
    destination: str
    status: str  # 'uploading' | 'completed' | 'cancelled' | 'failed'
    progress: float
    created_at: datetime
    updated_at: datetime

UPLOAD_BASE: Path = Path("backend") / "data" / "uploads"
UPLOAD_BASE.mkdir(parents=True, exist_ok=True)

_ACTIVE_TASKS: dict[str, _UploadTask] = {}
_HISTORY: list[_UploadTask] = []

# --------------- 公共小工具 ---------------
def _now() -> datetime:
    return datetime.utcnow()

async def _write_file_from_upload(upload: UploadFile, path: Path) -> int:
    """将 UploadFile 写入到目标路径，返回写入的字节总数"""
    total = 0
    # 使用二进制写入
    with path.open("wb") as f:
        while True:
            chunk = await upload.read(1024 * 1024)  # 1MB 一次
            if not chunk:
                break
            f.write(chunk)
            total += len(chunk)
    return total

# --------------- 数据模型 ---------------
class UploadSingleResponse(BaseModel):
    task_id: str
    filename: str
    status: str = Field("completed", description="上传状态")
    message: Optional[str] = None

class UploadBatchItem(BaseModel):
    task_id: str
    filename: str
    status: str
    message: Optional[str] = None

class UploadBatchResponse(BaseModel):
    tasks: List[UploadBatchItem]

class UploadProgress(BaseModel):
    task_id: str
    filename: str
    status: str
    progress: float

class UploadHistoryItem(BaseModel):
    task_id: str
    filename: str
    status: str
    created_at: datetime
    updated_at: datetime

class FolderUploadForm(BaseModel):
    folder_name: str = Field(..., description="目标文件夹名称")

# --------------- 路由实现 ---------------
@router.post("/single", response_model=UploadSingleResponse)
async def upload_single(
    file: UploadFile = File(...),
    folder: Optional[str] = Form(None, description="可选：目标文件夹名")
):
    """单文件上传
- 将上传的文件保存到 uploads/[folder]? 目录，并返回任务ID与状态"""
    task_id = str(uuid.uuid4())
    filename = file.filename
    dest_dir = UPLOAD_BASE
    if folder:
        dest_dir = dest_dir / folder
        dest_dir.mkdir(parents=True, exist_ok=True)
    dest_path = dest_dir / f"{task_id}_{filename}"

    task = _UploadTask(
        id=task_id,
        filename=filename,
        destination=str(dest_path),
        status="uploading",
        progress=0.0,
        created_at=_now(),
        updated_at=_now(),
    )
    _ACTIVE_TASKS[task_id] = task

    try:
        await _write_file_from_upload(file, dest_path)
        task.progress = 100.0
        task.status = "completed"
        task.updated_at = _now()
        _HISTORY.append(task)
        _ACTIVE_TASKS.pop(task_id, None)
        return UploadSingleResponse(task_id=task_id, filename=filename, status="completed")
    except Exception as exc:
        task.status = "failed"
        task.updated_at = _now()
        _HISTORY.append(task)
        _ACTIVE_TASKS.pop(task_id, None)
        raise HTTPException(status_code=500, detail=f"上传失败: {str(exc)}")


@router.post("/batch", response_model=UploadBatchResponse)
async def upload_batch(
    files: List[UploadFile] = File(...),
    folder: Optional[str] = Form(None, description="可选：目标文件夹名")
):
    """批量文件上传"""
    results: List[UploadBatchItem] = []
    for f in files:
        task_id = str(uuid.uuid4())
        filename = f.filename
        dest_dir = UPLOAD_BASE
        if folder:
            dest_dir = dest_dir / folder
            dest_dir.mkdir(parents=True, exist_ok=True)
        dest_path = dest_dir / f"{task_id}_{filename}"

        task = _UploadTask(
            id=task_id,
            filename=filename,
            destination=str(dest_path),
            status="uploading",
            progress=0.0,
            created_at=_now(),
            updated_at=_now(),
        )
        _ACTIVE_TASKS[task_id] = task
        try:
            await _write_file_from_upload(f, dest_path)
            task.progress = 100.0
            task.status = "completed"
            task.updated_at = _now()
            _HISTORY.append(task)
            _ACTIVE_TASKS.pop(task_id, None)
            results.append(UploadBatchItem(task_id=task_id, filename=filename, status="completed"))
        except Exception as exc:
            task.status = "failed"
            task.updated_at = _now()
            _HISTORY.append(task)
            _ACTIVE_TASKS.pop(task_id, None)
            results.append(UploadBatchItem(task_id=task_id, filename=filename, status="failed", message=str(exc)))
    return UploadBatchResponse(tasks=results)


@router.post("/folder", response_model=UploadBatchResponse)
async def upload_folder(
    files: List[UploadFile] = File(...),
    folder_name: str = Form(..., description="目标文件夹名称，用于保存上传内容的子路径")
):
    """文件夹上传
    - 将多个文件保存到 uploads/{folder_name}/，并保留原始文件名"""
    dest_root = UPLOAD_BASE / folder_name
    dest_root.mkdir(parents=True, exist_ok=True)
    results: List[UploadBatchItem] = []

    for f in files:
        task_id = str(uuid.uuid4())
        dest_path = dest_root / f"{task_id}_{f.filename}"
        task = _UploadTask(
            id=task_id,
            filename=f.filename,
            destination=str(dest_path),
            status="uploading",
            progress=0.0,
            created_at=_now(),
            updated_at=_now(),
        )
        _ACTIVE_TASKS[task_id] = task
        try:
            await _write_file_from_upload(f, dest_path)
            task.progress = 100.0
            task.status = "completed"
            task.updated_at = _now()
            _HISTORY.append(task)
            _ACTIVE_TASKS.pop(task_id, None)
            results.append(UploadBatchItem(task_id=task_id, filename=f.filename, status="completed"))
        except Exception as exc:
            task.status = "failed"
            task.updated_at = _now()
            _HISTORY.append(task)
            _ACTIVE_TASKS.pop(task_id, None)
            results.append(UploadBatchItem(task_id=task_id, filename=f.filename, status="failed", message=str(exc)))
    return UploadBatchResponse(tasks=results)


@router.get("/progress/{task_id}", response_model=UploadProgress)
async def get_progress(task_id: str):
    """上传进度查询
    - 根据 task_id 查询当前任务状态与进度"""
    task = _ACTIVE_TASKS.get(task_id)
    if not task:
        # 从历史中查询
        for h in reversed(_HISTORY):
            if h.id == task_id:
                return UploadProgress(
                    task_id=task_id,
                    filename=h.filename,
                    status=h.status,
                    progress=h.progress,
                )
        raise HTTPException(status_code=404, detail=f"找不到任务 {task_id}")
    return UploadProgress(
        task_id=task.id,
        filename=task.filename,
        status=task.status,
        progress=task.progress,
    )


@router.post("/cancel/{task_id}", response_model=UploadSingleResponse)
async def cancel_upload(task_id: str):
    """取消上传"""
    task = _ACTIVE_TASKS.pop(task_id, None)
    if not task:
        raise HTTPException(status_code=404, detail=f"找不到正在进行的上传任务 {task_id}")
    task.status = "cancelled"
    task.updated_at = _now()
    _HISTORY.append(task)
    return UploadSingleResponse(task_id=task_id, filename=task.filename, status="cancelled")


@router.get("/history", response_model=List[UploadHistoryItem])
async def history_uploads():
    """上传历史查询
    - 返回所有历史记录"""
    return [
        UploadHistoryItem(
            task_id=h.id,
            filename=h.filename,
            status=h.status,
            created_at=h.created_at,
            updated_at=h.updated_at,
        )
        for h in _HISTORY
    ]
