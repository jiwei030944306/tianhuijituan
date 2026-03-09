"""
文件夹操作工具函数
用于生成批次文件夹、管理operations.json文件
"""
import os
import json
import random
import string
import shutil
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
from pathlib import Path

# 配置日志
logger = logging.getLogger(__name__)

# 计算项目根目录
# __file__ = backend/app/utils/folder_utils.py
# .parent = backend/app/utils/
# .parent.parent = backend/app/
# .parent.parent.parent = backend/
# .parent.parent.parent.parent = 项目根目录/
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent

# 上传根目录（使用项目data目录）
UPLOAD_ROOT = Path(r"D:\newAI\天卉题云智研\data\uploads")

# 确保上传目录存在
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
logger.info(f"上传根目录: {UPLOAD_ROOT}")


def generate_random_code(length: int = 6) -> str:
    """
    生成指定长度的随机字母数字组合
    
    Args:
        length: 长度，默认6位
        
    Returns:
        随机字符串，如：a7x9k2
    """
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choices(chars, k=length))


def generate_batch_id() -> str:
    """
    生成批次ID
    格式：YYYYMMDD-HHMMSS-XXXXXX
    
    Returns:
        批次ID字符串，如：20260201-143000-a7x9k2
    """
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")
    random_code = generate_random_code(6)
    return f"{date_str}-{time_str}-{random_code}"


def get_main_folder_path(subject_code: str) -> str:
    """
    获取主文件夹路径

    Args:
        subject_code: 学科代码，如：math, math2, physics, physics2

    Returns:
        主文件夹完整路径，如：data/uploads/math/
    """
    return os.path.join(UPLOAD_ROOT, subject_code)


def get_batch_folder_path(subject_code: str, batch_id: str) -> str:
    """
    获取批次文件夹路径

    Args:
        subject_code: 学科代码
        batch_id: 批次ID

    Returns:
        批次文件夹完整路径，如：data/uploads/math/20260201-143000-a7x9k2/
    """
    return os.path.join(get_main_folder_path(subject_code), batch_id)


def ensure_folder_exists(folder_path: str) -> str:
    """
    确保文件夹存在，不存在则创建
    
    Args:
        folder_path: 文件夹路径
        
    Returns:
        文件夹路径
    """
    Path(folder_path).mkdir(parents=True, exist_ok=True)
    return folder_path


def get_operations_file_path(subject_code: str, record_date: date) -> str:
    """
    获取 operations.json 文件路径

    Args:
        subject_code: 学科代码
        record_date: 记录日期

    Returns:
        operations.json 文件路径，如：uploads/math/operations-20260201.json
    """
    main_folder = get_main_folder_path(subject_code)
    date_str = record_date.strftime("%Y%m%d")
    return os.path.join(main_folder, f"operations-{date_str}.json")


def read_operations_json(subject_code: str, record_date: date) -> Optional[Dict[str, Any]]:
    """
    读取 operations.json 文件

    Args:
        subject_code: 学科代码
        record_date: 记录日期

    Returns:
        JSON内容字典，文件不存在返回 None
    """
    file_path = get_operations_file_path(subject_code, record_date)

    if not os.path.exists(file_path):
        return None

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"读取 operations.json 失败: {e}")
        return None


def write_operations_json(
    subject_code: str,
    record_date: date,
    record: Dict[str, Any]
) -> str:
    """
    写入或更新 operations.json 文件（简化版）

    只需传入 subject_code，其他信息自动推导

    Args:
        subject_code: 学科代码 (math/math2/physics/...)
        record_date: 记录日期
        record: 单条上传记录

    Returns:
        文件路径
    """
    from app.constants.subject import get_subject_name, get_education_level

    # 自动推导学科信息
    subject_name = get_subject_name(subject_code)
    education_level = get_education_level(subject_code)

    # 确保主文件夹存在
    main_folder = ensure_folder_exists(get_main_folder_path(subject_code))

    file_path = get_operations_file_path(subject_code, record_date)

    # 读取现有内容或创建新内容
    data = read_operations_json(subject_code, record_date)

    if data is None:
        # 创建新文件（优化后的结构）
        data = {
            "subject_code": subject_code,
            "subject_name": subject_name,
            "education_level": education_level,
            "date": record_date.strftime("%Y-%m-%d"),
            "total_uploads": 0,
            "last_updated": datetime.now().isoformat(),
            "records": []
        }

    # 追加新记录
    data["records"].append(record)
    data["total_uploads"] = len(data["records"])
    data["last_updated"] = datetime.now().isoformat()

    # 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return file_path


def create_batch_folder(subject_code: str, batch_id: str) -> str:
    """
    创建批次文件夹

    Args:
        subject_code: 学科代码
        batch_id: 批次ID

    Returns:
        批次文件夹路径
    """
    batch_path = get_batch_folder_path(subject_code, batch_id)
    return ensure_folder_exists(batch_path)


def get_all_operations_files(subject_code: str) -> List[str]:
    """
    获取指定学科下的所有 operations-*.json 文件路径

    Args:
        subject_code: 学科代码

    Returns:
        operations-*.json 文件路径列表，按日期倒序排序
    """
    import glob

    main_folder = get_main_folder_path(subject_code)

    if not os.path.exists(main_folder):
        return []

    pattern = os.path.join(main_folder, "operations-*.json")
    files = glob.glob(pattern)

    # 按文件名排序（日期倒序）
    files.sort(reverse=True)

    return files


def delete_batch_folder(subject_code: str, batch_id: str) -> bool:
    """
    删除批次文件夹

    Args:
        subject_code: 学科代码
        batch_id: 批次ID

    Returns:
        是否成功删除
    """
    batch_path = get_batch_folder_path(subject_code, batch_id)

    if not os.path.exists(batch_path):
        return False

    try:
        shutil.rmtree(batch_path)
        logger.info(f"成功删除批次文件夹: {batch_path}")
        return True
    except Exception as e:
        logger.error(f"删除批次文件夹失败: {e}")
        return False


def remove_record_from_operations_json(subject_code: str, batch_id: str) -> bool:
    """
    从 operations.json 中删除指定批次的记录

    Args:
        subject_code: 学科代码
        batch_id: 批次ID

    Returns:
        是否成功删除
    """
    import glob

    main_folder = get_main_folder_path(subject_code)

    if not os.path.exists(main_folder):
        return False

    # 查找所有 operations-*.json 文件
    pattern = os.path.join(main_folder, "operations-*.json")
    files = glob.glob(pattern)

    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 过滤掉要删除的批次记录
            original_count = len(data.get("records", []))
            data["records"] = [r for r in data.get("records", []) if r.get("batch_id") != batch_id]
            data["total_uploads"] = len(data["records"])
            data["last_updated"] = datetime.now().isoformat()

            # 如果没有记录了，删除文件
            if len(data["records"]) == 0:
                os.remove(file_path)
                logger.info(f"删除空的 operations 文件: {file_path}")
                return True

            # 如果有变化，更新文件
            if len(data["records"]) != original_count:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                logger.info(f"从 {file_path} 中删除批次 {batch_id}")
                return True

        except Exception as e:
            logger.error(f"更新 operations.json 失败 ({file_path}): {e}")
            continue

    return False
