"""
测试上传历史记录API
"""
import os
import json
import pytest
from datetime import datetime
from fastapi.testclient import TestClient
from app.main import app
from app.utils.folder_utils import get_main_folder_path, get_all_operations_files

client = TestClient(app)


def test_get_upload_history_success():
    """测试成功获取历史记录"""
    # 使用已存在的测试数据
    folder_code = "m7s9m2"
    
    response = client.get(f"/api/questions/upload-history?folder_code={folder_code}")
    
    assert response.status_code == 200
    data = response.json()
    
    # 验证响应结构
    assert "folder_code" in data
    assert "education_level" in data
    assert "subject" in data
    assert "total_uploads" in data
    assert "records" in data
    
    # 验证数据类型
    assert isinstance(data["records"], list)
    assert isinstance(data["total_uploads"], int)
    
    # 验证记录按时间倒序排序
    records = data["records"]
    for i in range(len(records) - 1):
        assert records[i]["timestamp"] >= records[i + 1]["timestamp"]


def test_get_upload_history_empty_directory():
    """测试空目录的处理"""
    folder_code = "nonexistent_test_code"
    
    response = client.get(f"/api/questions/upload-history?folder_code={folder_code}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_uploads"] == 0
    assert len(data["records"]) == 0


def test_get_upload_history_missing_param():
    """测试缺少参数的情况"""
    response = client.get("/api/questions/upload-history")
    
    assert response.status_code == 422  # 参数验证失败


def test_operations_json_format():
    """测试 operations.json 格式是否正确"""
    folder_code = "m7s9m2"
    operations_files = get_all_operations_files(folder_code)
    
    if operations_files:
        for file_path in operations_files:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                assert "records" in data, "缺少 records 字段"
                assert isinstance(data["records"], list), "records 应该是列表"


def test_record_fields_completeness():
    """测试记录字段是否完整"""
    folder_code = "m7s9m2"
    response = client.get(f"/api/questions/upload-history?folder_code={folder_code}")
    data = response.json()
    records = data["records"]
    
    if records:
        required_fields = [
            "batch_id", "timestamp", "teacher_name",
            "display_name", "file_count", "image_count", "status"
        ]
        
        for record in records:
            for field in required_fields:
                assert field in record, f"缺少必填字段: {field}"


def test_get_all_operations_files():
    """测试获取所有 operations 文件"""
    folder_code = "m7s9m2"
    files = get_all_operations_files(folder_code)
    
    assert isinstance(files, list)
    
    # 验证文件路径格式
    for file_path in files:
        assert "operations-" in os.path.basename(file_path)
        assert file_path.endswith(".json")


def test_api_response_time():
    """测试API响应时间"""
    import time
    
    folder_code = "m7s9m2"
    start_time = time.time()
    
    response = client.get(f"/api/questions/upload-history?folder_code={folder_code}")
    
    end_time = time.time()
    response_time = end_time - start_time
    
    assert response.status_code == 200
    assert response_time < 1.0, f"API响应时间过长: {response_time:.2f}秒"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])