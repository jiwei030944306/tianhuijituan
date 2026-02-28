"""
P2 Step 1: 脚本质检服务
对批次试题进行质量检查，标记状态，归档废题

质检规则：
- 题干缺失 → waste
- 选择题选项缺失/不足 → waste
- 图片路径错误 → 尝试修复 → 失败标 error
- 正常 → active
"""
import os
import json
import logging
from datetime import date

logger = logging.getLogger(__name__)

# 选择题类型集合（中文 + 英文兼容）
CHOICE_TYPES = {"选择题", "多选题", "single_choice", "multiple_choice"}


def quality_check_batch(
    questions: list[dict],
    batch_id: str,
    content_dir: str
) -> dict[str, list[dict]]:
    """
    对批次内所有题目执行 Step1 质检

    直接修改传入的 question dict，并按状态分组返回
    返回: {"active": [...], "waste": [...]}
    """
    active = []
    waste = []

    for i, q in enumerate(questions):
        _check_single(q, batch_id, i, content_dir)

        if q["status"] == "waste":
            waste.append(q)
        else:
            active.append(q)

    logger.info(
        f"批次 {batch_id} 质检完成: "
        f"{len(active)} 正常, {len(waste)} 废题"
    )
    return {"active": active, "waste": waste}


def _check_single(q: dict, batch_id: str, index: int, content_dir: str):
    """质检单道题，直接修改传入的 dict"""
    fatal = []   # 不可修复 → waste
    errors = []  # 可修复 → error

    # --- 补齐基础标识 ---
    if not q.get("id"):
        q["id"] = f"{batch_id}-Q{index + 1:03d}"
    if not q.get("questionNumber"):
        q["questionNumber"] = index + 1

    # --- 核心字段检测 ---

    # 1. 题干
    if not q.get("stem", "").strip():
        fatal.append("题干缺失")

    # 2. 选项（选择题必须 >= 2 个有效选项）
    q_type = q.get("type", "")
    if q_type in CHOICE_TYPES:
        opts = q.get("options", [])
        if not opts or len(opts) < 2:
            fatal.append("选择题选项缺失")
        else:
            empty = [
                opt.get("key", f"选项{j+1}")
                for j, opt in enumerate(opts)
                if not opt.get("content", "").strip()
            ]
            if empty:
                errors.append(f"选项内容为空: {', '.join(empty)}")

    # 3. 图片路径检测 + 修复尝试
    stem_images = q.get("stemImages", [])
    if stem_images:
        images_dir = os.path.join(content_dir, "images")
        missing = []
        for img in stem_images:
            img_src = img.get("src", "")
            if not img_src:
                continue
            # 提取文件名（处理 ./xxx.jpg 或 images/xxx.jpg 格式）
            img_name = os.path.basename(
                img_src.replace("./", "").replace("images/", "")
            )
            if not os.path.exists(os.path.join(images_dir, img_name)):
                fixed = _try_fix_image(images_dir, img_name)
                if fixed:
                    img["src"] = fixed  # 修复成功，更新路径
                else:
                    missing.append(img_name)
        if missing:
            errors.append(f"图片文件缺失: {', '.join(missing[:3])}")

    # --- 补齐非核心字段默认值 ---
    q.setdefault("answer", "")
    q.setdefault("analysis", "")
    q.setdefault("options", [])
    q.setdefault("stemImages", [])
    q.setdefault("topics", [])
    q.setdefault("comment", "")

    # --- 初始化 AI 准备字段 ---
    q.setdefault("isAiOptimized", False)
    q.setdefault("aiModel", "")
    q.setdefault("aiOptimizedAt", "")

    # --- 设置状态 ---
    if fatal:
        q["status"] = "waste"
        q["statusMessage"] = "; ".join(fatal)
    elif errors:
        q["status"] = "error"
        q["statusMessage"] = "; ".join(errors)
    else:
        q.setdefault("status", "active")

    # 标记已质检
    q["_qualityChecked"] = True


def _try_fix_image(images_dir: str, img_name: str) -> str | None:
    """在 images/ 目录中模糊匹配图片文件名（忽略扩展名大小写）"""
    if not os.path.exists(images_dir):
        return None
    name_base = os.path.splitext(img_name)[0].lower()
    for f in os.listdir(images_dir):
        if os.path.splitext(f)[0].lower() == name_base:
            return f
    return None


def archive_waste(waste_questions: list[dict], content_dir: str) -> int:
    """
    归档废题到 waste-YYYYMMDD.json
    按 id 去重，返回新增归档数量
    """
    if not waste_questions:
        return 0

    filename = f"waste-{date.today().strftime('%Y%m%d')}.json"
    filepath = os.path.join(content_dir, filename)

    # 追加模式：同一天可能多次质检
    existing = []
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            existing = json.loads(f.read())

    # 按 id 去重
    existing_ids = {q.get("id") for q in existing}
    new_waste = [q for q in waste_questions if q.get("id") not in existing_ids]
    existing.extend(new_waste)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(json.dumps(existing, ensure_ascii=False, indent=2))

    logger.info(f"归档 {len(new_waste)} 道废题到 {filename}")
    return len(new_waste)


def convert_image_urls(questions: list[dict], batch_id: str):
    """
    将图片路径转换为 API URL（仅用于响应，不持久化）
    ./xxx.jpg → /api/questions/batch/{batch_id}/image/xxx.jpg
    """
    for q in questions:
        for img in q.get("stemImages", []):
            src = img.get("src", "")
            if src and not src.startswith("/api/"):
                img_name = os.path.basename(src)
                img["src"] = f"/api/questions/batch/{batch_id}/image/{img_name}"
