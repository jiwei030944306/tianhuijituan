"""
Quality Check Service Unit Tests

This module contains unit tests for the quality_check service.
"""

import pytest
import os
import json
import tempfile
from datetime import date
from unittest.mock import patch, MagicMock

# Import the service functions
from backend.app.services.quality_check import (
    quality_check_batch,
    _check_single,
    _try_fix_image,
    archive_waste,
    convert_image_urls,
    CHOICE_TYPES
)


class TestQualityCheckBatch:
    """Tests for quality_check_batch function"""
    
    def test_empty_questions_list(self, tmp_path):
        """Test with empty questions list"""
        result = quality_check_batch([], "batch-001", str(tmp_path))
        assert result == {"active": [], "waste": []}
    
    def test_valid_question_becomes_active(self, tmp_path):
        """Test valid question is marked as active"""
        questions = [{
            "stem": "What is the capital of France?",
            "type": "single_choice",
            "options": [
                {"key": "A", "content": "Paris"},
                {"key": "B", "content": "London"}
            ],
            "answer": "A"
        }]
        
        result = quality_check_batch(questions, "batch-001", str(tmp_path))
        
        assert len(result["active"]) == 1
        assert len(result["waste"]) == 0
        assert result["active"][0]["status"] == "active"
        assert result["active"][0].get("_qualityChecked") is True
    
    def test_missing_stem_becomes_waste(self, tmp_path):
        """Test question with missing stem is marked as waste"""
        questions = [{
            "stem": "",
            "type": "single_choice",
            "options": [
                {"key": "A", "content": "Option A"}
            ]
        }]
        
        result = quality_check_batch(questions, "batch-001", str(tmp_path))
        
        assert len(result["active"]) == 0
        assert len(result["waste"]) == 1
        assert result["waste"][0]["status"] == "waste"
        assert "题干缺失" in result["waste"][0]["statusMessage"]
    
    def test_choice_question_missing_options_becomes_waste(self, tmp_path):
        """Test choice question with insufficient options is marked as waste"""
        questions = [{
            "stem": "What is 2+2?",
            "type": "single_choice",
            "options": [],
            "answer": "4"
        }]
        
        result = quality_check_batch(questions, "batch-001", str(tmp_path))
        
        assert len(result["waste"]) == 1
        assert "选项缺失" in result["waste"][0]["statusMessage"]


class TestCheckSingle:
    """Tests for _check_single function"""
    
    def test_auto_assigns_id_and_question_number(self, tmp_path):
        """Test that id and questionNumber are auto-assigned"""
        q = {
            "stem": "Test question",
            "type": "single_choice",
            "options": [{"key": "A", "content": "Test"}]
        }
        
        _check_single(q, "batch-001", 5, str(tmp_path))
        
        assert q["id"] == "batch-001-Q006"
        assert q["questionNumber"] == 6
    
    def test_preserves_existing_id(self, tmp_path):
        """Test that existing id is preserved"""
        q = {
            "id": "custom-id-123",
            "stem": "Test question",
            "type": "single_choice",
            "options": [{"key": "A", "content": "Test"}]
        }
        
        _check_single(q, "batch-001", 0, str(tmp_path))
        
        assert q["id"] == "custom-id-123"


class TestTryFixImage:
    """Tests for _try_fix_image function"""
    
    def test_exact_match_found(self, tmp_path):
        """Test exact filename match"""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "test_image.jpg").write_text("fake image")
        
        result = _try_fix_image(str(images_dir), "test_image.jpg")
        
        assert result == "test_image.jpg"
    
    def test_case_insensitive_match(self, tmp_path):
        """Test case-insensitive filename match"""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "Test_Image.JPG").write_text("fake image")
        
        result = _try_fix_image(str(images_dir), "test_image.jpg")
        
        assert result == "Test_Image.JPG"
    
    def test_no_match_returns_none(self, tmp_path):
        """Test when no match is found"""
        images_dir = tmp_path / "images"
        images_dir.mkdir()
        (images_dir / "other_image.jpg").write_text("fake image")
        
        result = _try_fix_image(str(images_dir), "nonexistent.jpg")
        
        assert result is None
    
    def test_nonexistent_directory_returns_none(self):
        """Test when images directory doesn't exist"""
        result = _try_fix_image("/nonexistent/path", "test.jpg")
        
        assert result is None


class TestArchiveWaste:
    """Tests for archive_waste function"""
    
    def test_empty_list_returns_zero(self, tmp_path):
        """Test with empty waste list"""
        result = archive_waste([], str(tmp_path))
        
        assert result == 0
    
    def test_creates_new_file(self, tmp_path):
        """Test creating new archive file"""
        waste = [
            {"id": "q1", "stem": "Test 1", "status": "waste"},
            {"id": "q2", "stem": "Test 2", "status": "waste"}
        ]
        
        result = archive_waste(waste, str(tmp_path))
        
        assert result == 2
        
        today = date.today().strftime('%Y%m%d')
        filepath = tmp_path / f"waste-{today}.json"
        assert filepath.exists()
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 2
    
    def test_deduplicates_by_id(self, tmp_path):
        """Test that questions with same id are deduplicated"""
        # First batch
        waste1 = [
            {"id": "q1", "stem": "Test 1", "status": "waste"}
        ]
        archive_waste(waste1, str(tmp_path))
        
        # Second batch with same id
        waste2 = [
            {"id": "q1", "stem": "Duplicate", "status": "waste"},
            {"id": "q2", "stem": "New", "status": "waste"}
        ]
        result = archive_waste(waste2, str(tmp_path))
        
        assert result == 1  # Only q2 is new
        
        today = date.today().strftime('%Y%m%d')
        filepath = tmp_path / f"waste-{today}.json"
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 2
        
        # Original q1 should be preserved
        q1 = next(q for q in data if q["id"] == "q1")
        assert q1["stem"] == "Test 1"


class TestConvertImageUrls:
    """Tests for convert_image_urls function"""
    
    def test_converts_relative_paths(self):
        """Test converting relative image paths to API URLs"""
        questions = [
            {
                "stemImages": [
                    {"src": "./image1.jpg"},
                    {"src": "images/image2.png"}
                ]
            }
        ]
        
        convert_image_urls(questions, "batch-123")
        
        assert questions[0]["stemImages"][0]["src"] == "/api/questions/batch/batch-123/image/image1.jpg"
        assert questions[0]["stemImages"][1]["src"] == "/api/questions/batch/batch-123/image/image2.png"
    
    def test_skips_api_urls(self):
        """Test that existing API URLs are not modified"""
        questions = [
            {
                "stemImages": [
                    {"src": "/api/existing/path/image.jpg"}
                ]
            }
        ]
        
        convert_image_urls(questions, "batch-123")
        
        assert questions[0]["stemImages"][0]["src"] == "/api/existing/path/image.jpg"
    
    def test_empty_images_list(self):
        """Test with empty stemImages list"""
        questions = [
            {
                "stemImages": []
            }
        ]
        
        convert_image_urls(questions, "batch-123")
        
        assert questions[0]["stemImages"] == []


class TestChoiceTypes:
    """Tests for CHOICE_TYPES constant"""
    
    def test_choice_types_defined(self):
        """Test that CHOICE_TYPES is properly defined"""
        assert isinstance(CHOICE_TYPES, set)
        assert "选择题" in CHOICE_TYPES
        assert "多选题" in CHOICE_TYPES
        assert "single_choice" in CHOICE_TYPES
        assert "multiple_choice" in CHOICE_TYPES
