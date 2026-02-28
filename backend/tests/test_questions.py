"""
题目 API 测试 - 使用数据库隔离
"""
import pytest
from httpx import AsyncClient


class TestQuestionsAPI:
    """题目 API 测试类"""

    @pytest.mark.asyncio
    async def test_get_questions_success(self, client: AsyncClient):
        """测试获取题目列表 - 成功场景"""
        response = await client.get("/api/questions/")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_questions_with_pagination(self, client: AsyncClient):
        """测试分页查询"""
        response = await client.get("/api/questions/?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 5

    @pytest.mark.asyncio
    async def test_get_questions_with_filter(self, client: AsyncClient):
        """测试筛选查询"""
        response = await client.get("/api/questions/?type=single_choice")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    @pytest.mark.asyncio
    async def test_get_question_by_id_not_found(self, client: AsyncClient):
        """测试获取不存在的题目"""
        response = await client.get("/api/questions/nonexistent-id")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_create_question_success(
        self,
        client: AsyncClient,
        sample_question_data: dict
    ):
        """测试创建题目 - 成功场景"""
        response = await client.post("/api/questions/", json=sample_question_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["stem"] == sample_question_data["stem"]

    @pytest.mark.asyncio
    async def test_create_question_missing_required_field(self, client: AsyncClient):
        """测试创建题目 - 缺少必填字段"""
        question_data = {
            "type": "single_choice",
            # 缺少必填的 stem 和 answer
        }
        response = await client.post("/api/questions/", json=question_data)
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_update_question_success(
        self,
        client: AsyncClient,
        sample_question_data: dict
    ):
        """测试更新题目 - 成功场景"""
        # 先创建题目
        create_response = await client.post("/api/questions/", json=sample_question_data)
        assert create_response.status_code == 201
        question_id = create_response.json()["id"]

        # 更新题目
        update_data = {"stem": "更新后的题目"}
        response = await client.put(f"/api/questions/{question_id}", json=update_data)
        assert response.status_code == 200
        data = response.json()
        assert data["stem"] == "更新后的题目"

    @pytest.mark.asyncio
    async def test_update_question_not_found(self, client: AsyncClient):
        """测试更新不存在的题目"""
        update_data = {"stem": "更新后的题目"}
        response = await client.put("/api/questions/nonexistent-id", json=update_data)
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_question_success(
        self,
        client: AsyncClient,
        sample_question_data: dict
    ):
        """测试删除题目 - 成功场景"""
        # 先创建题目
        create_response = await client.post("/api/questions/", json=sample_question_data)
        assert create_response.status_code == 201
        question_id = create_response.json()["id"]

        # 删除题目
        response = await client.delete(f"/api/questions/{question_id}")
        assert response.status_code == 204

        # 验证已删除
        get_response = await client.get(f"/api/questions/{question_id}")
        assert get_response.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_question_not_found(self, client: AsyncClient):
        """测试删除不存在的题目"""
        response = await client.delete("/api/questions/nonexistent-id")
        assert response.status_code == 404


class TestHealthCheck:
    """健康检查测试"""

    @pytest.mark.asyncio
    async def test_root(self, client: AsyncClient):
        """测试根路径"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "智研题库云系统 API"

    @pytest.mark.asyncio
    async def test_health_check(self, client: AsyncClient):
        """测试健康检查"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
