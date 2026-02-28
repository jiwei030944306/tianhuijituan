"""
上传 API 测试
"""
import pytest
from httpx import AsyncClient


class TestUploadAPI:
    """上传 API 测试"""

    @pytest.mark.asyncio
    async def test_get_upload_history_empty(self, client: AsyncClient):
        """测试获取上传历史 - 空结果"""
        response = await client.get("/api/questions/upload-history?folder_code=unknown")
        assert response.status_code == 200
        data = response.json()
        assert "records" in data
        assert isinstance(data["records"], list)

    @pytest.mark.asyncio
    async def test_get_statistics(self, client: AsyncClient):
        """测试获取统计数据"""
        response = await client.get("/api/questions/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "by_type" in data
