"""导入测试数据到数据库"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.models.question import Question


async def import_test_batch(json_path: str):
    """导入测试批次数据"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    batch_id = data.get('batch_id')
    folder_code = data.get('folder_code')
    education_level = data.get('education_level')
    subject = data.get('subject')
    questions = data.get('questions', [])

    print(f"导入批次: {batch_id}")
    print(f"学段: {education_level}, 学科: {subject}")
    print(f"题目数量: {len(questions)}")

    async with AsyncSessionLocal() as session:
        imported = 0
        for q in questions:
            # 检查是否已存在
            from sqlalchemy import select
            result = await session.execute(select(Question).where(Question.id == q['id']))
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  跳过已存在: {q['id']}")
                continue

            question = Question(
                id=q['id'],
                question_number=q.get('questionNumber', 1),
                type=str(q.get('type', 1)),  # 数字题型值
                difficulty=q.get('difficulty'),
                status=q.get('status', 'active'),
                stem=q.get('stem', ''),
                options=json.dumps(q.get('options', []), ensure_ascii=False) if q.get('options') else None,
                answer=q.get('answer', ''),
                analysis=q.get('analysis'),
                topics=json.dumps(q.get('topics', []), ensure_ascii=False) if q.get('topics') else None,
                category=q.get('category'),
                subject=subject,
                education_level=education_level,
                source_folder=folder_code,
                source=batch_id,
            )
            session.add(question)
            imported += 1

        await session.commit()
        print(f"成功导入: {imported} 道题目")


async def main():
    # 导入测试批次1 (初中数学)
    await import_test_batch(
        r"D:\newAI\天卉题云智研\data\uploads\wks_m7s9m2\test_batch_001\questions.json"
    )

    # 导入测试批次2 (高中数学)
    await import_test_batch(
        r"D:\newAI\天卉题云智研\data\uploads\g10m_s1\test_batch_002\questions.json"
    )


if __name__ == "__main__":
    asyncio.run(main())