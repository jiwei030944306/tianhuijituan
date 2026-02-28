"""导入题目数据"""
import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import AsyncSessionLocal
from app.models.question import Question

async def import_question(json_file: str):
    """导入单个题目"""
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # 转换数据格式
    question = Question(
        id=data['id'],
        question_number=data['questionNumber'],
        type=data['type'],
        difficulty=data.get('difficulty') or data.get('aiDifficulty'),
        status=data.get('status', 'active'),
        stem=data['stem'],
        options=json.dumps(data.get('options', []), ensure_ascii=False),
        stem_images=json.dumps(data.get('stemImages', []), ensure_ascii=False),
        topics=json.dumps(data.get('topics') or data.get('aiTopics', []), ensure_ascii=False),
        category=data.get('category') or data.get('aiCategory'),
        answer=data.get('answer') or data.get('aiAnswer', ''),
        analysis=data.get('analysis') or data.get('aiAnalysis'),
        comment=data.get('comment'),
        status_message=data.get('statusMessage'),
        ai_grade=str(data.get('aiGrade')) if data.get('aiGrade') else None,
        ai_difficulty=data.get('aiDifficulty'),
        ai_topics=json.dumps(data.get('aiTopics', []), ensure_ascii=False),
        ai_category=data.get('aiCategory'),
        ai_analysis=data.get('aiAnalysis'),
        ai_model=data.get('aiModel'),
        ai_optimized_at=datetime.fromisoformat(data['aiOptimizedAt'].replace('+08:00', '')) if data.get('aiOptimizedAt') else None,
        is_ai_optimized=1 if data.get('isAiOptimized') else 0,
        confirmed_at=datetime.fromisoformat(data['confirmedAt'].replace('+08:00', '')) if data.get('confirmedAt') else None,
        subject=data.get('subject'),
        grade=data.get('grade') or data.get('aiGrade'),
        education_level=data.get('educationLevel'),
        source_folder=data.get('sourceFolder'),
        source=data.get('source'),
        version=data.get('version', 1),
        created_at=datetime.fromisoformat(data['createdAt'].replace('+08:00', '')) if data.get('createdAt') else None,
        updated_at=datetime.fromisoformat(data['updatedAt'].replace('+08:00', '')) if data.get('updatedAt') else None,
    )
    
    async with AsyncSessionLocal() as session:
        session.add(question)
        await session.commit()
        print(f"Success: Imported question {question.id}")

if __name__ == "__main__":
    json_file = r"D:\newAI\天卉题云智研\入录数据\九年级一阶模拟试题---吴倩_01.json"
    asyncio.run(import_question(json_file))
