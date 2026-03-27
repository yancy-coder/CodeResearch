"""Tests for coding service."""
import pytest
from unittest.mock import Mock, MagicMock

from services.coding_service import CodingService, CodingResult
from repositories.code_repository import CodeEntity
from CodeEngine.ir.code_ir import TextSegment


@pytest.fixture
def mock_repositories():
    return {
        'code': Mock(),
        'category': Mock(),
        'session': Mock()
    }


@pytest.fixture
def mock_engines():
    return {
        'open_coding': Mock(),
        'axial_coding': Mock(),
        'selective_coding': Mock()
    }


@pytest.fixture
def service(mock_repositories, mock_engines):
    return CodingService(
        code_repo=mock_repositories['code'],
        category_repo=mock_repositories['category'],
        session_repo=mock_repositories['session'],
        engines=mock_engines
    )


def test_open_coding_workflow(service, mock_engines, mock_repositories):
    from CodeEngine.ir.code_ir import CodeUnit, CodeSource
    
    segment = TextSegment(id="s1", content="测试文本", source="test.txt", position=(0, 8))
    mock_code = Mock()
    mock_code.id = "c1"
    mock_code.code_label = "代码1"
    mock_code.code_definition = "定义1"
    mock_code.created_by = CodeSource.AI
    mock_code.confidence = 0.9
    
    mock_engines['open_coding'].batch_code.return_value = {
        'approved_codes': [mock_code],
        'pending_reviews': []
    }
    
    result = service.run_open_coding([segment])
    
    assert result.success is True
    mock_engines['open_coding'].batch_code.assert_called_once()
    mock_repositories['code'].save.assert_called()


def test_full_coding_pipeline(service, mock_engines):
    from CodeEngine.ir.code_ir import CodeUnit, CodeSource
    
    segments = [TextSegment(id="s1", content="文本1", source="t.txt", position=(0, 3))]
    
    mock_code = Mock()
    mock_code.id = "c1"
    mock_code.code_label = "代码"
    mock_code.code_definition = "定义"
    mock_code.created_by = CodeSource.AI
    
    mock_engines['open_coding'].batch_code.return_value = {
        'approved_codes': [mock_code],
        'pending_reviews': []
    }
    mock_engines['axial_coding'].categorize_codes.return_value = []
    mock_engines['selective_coding'].identify_core_category.return_value = None
    
    result = service.run_full_pipeline(segments)
    
    assert result.success is True
    mock_engines['open_coding'].batch_code.assert_called_once()
    mock_engines['axial_coding'].categorize_codes.assert_called_once()


def test_missing_engine_error(service):
    service.engines = {}  # No engines
    
    result = service.run_open_coding([])
    
    assert result.success is False
    assert "not available" in result.message


def test_get_coding_status(service, mock_repositories):
    mock_repositories['code'].list.return_value = [
        CodeEntity(id="c1", label="A", level="open"),
        CodeEntity(id="c2", label="B", level="axial")
    ]
    mock_repositories['category'].list.return_value = []
    
    status = service.get_coding_status()
    
    assert status['total_codes'] == 2
    assert status['open_codes'] == 1
    assert status['axial_codes'] == 1
