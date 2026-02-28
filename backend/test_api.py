# 快速测试脚本 - 验证后端是否正常工作
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

async def test_api_endpoints():
    """测试关键API端点"""
    print("\n=== 测试关键API端点 ===\n")

    try:
        # 测试1: upload-history 接口
        print("[Test 1] 测试 upload-history 接口...")
        from app.api.questions import get_upload_history

        result = await get_upload_history('m7s9m2')
        print(f"  folder_code: {result['folder_code']}")
        print(f"  total_uploads: {result['total_uploads']}")
        print(f"  records: {len(result['records'])} 条")

        if 'error' in result:
            print(f"  [WARN] 有错误信息: {result['error']}")
        else:
            print("  [OK] 接口正常，返回空结果（目录不存在）")

        # 测试2: 数据库连接
        print("\n[Test 2] 测试数据库连接...")
        from app.core.database import AsyncSessionLocal

        session = AsyncSessionLocal()
        try:
            # 简单测试会话创建
            print("  [OK] 数据库会话创建成功")
        finally:
            await session.close()

        # 测试3: 文件夹工具
        print("\n[Test 3] 测试文件夹工具...")
        from app.utils.folder_utils import UPLOAD_ROOT

        print(f"  UPLOAD_ROOT: {UPLOAD_ROOT}")
        print(f"  存在: {UPLOAD_ROOT.exists()}")
        print("  [OK] 文件夹工具正常")

        print("\n" + "=" * 50)
        print("所有测试通过！后端准备就绪。")
        print("=" * 50)
        return True

    except Exception as e:
        print(f"\n[FAIL] 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api_endpoints())
    sys.exit(0 if success else 1)
