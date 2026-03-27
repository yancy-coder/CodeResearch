"""Tests for import service."""
import pytest
from unittest.mock import Mock

from services.import_service import ImportService
from CodeEngine.ir.code_ir import TextSegment


@pytest.fixture
def service():
    import_engine = Mock()
    session_repo = Mock()
    return ImportService(import_engine, session_repo)


def test_import_file(service):
    # Mock segments
    mock_segments = [
        TextSegment(id="s1", content="文本1", source="t.txt", position=(0, 3))
    ]
    service.import_engine.import_file.return_value = mock_segments
    
    # Mock session (doesn't exist yet)
    service.session_repo.get.return_value = None
    
    # Execute
    result = service.import_file("test.txt", segment_type="paragraph")
    
    # Verify
    assert len(result) == 1
    assert result[0].id == "s1"
    service.import_engine.import_file.assert_called_once()
    service.session_repo.save.assert_called_once()


def test_import_file_with_existing_session(service):
    from repositories.session_repository import SessionEntity
    
    # Mock existing session
    existing_session = SessionEntity(id="default", data={"existing": "data"})
    service.session_repo.get.return_value = existing_session
    
    mock_segments = [
        TextSegment(id="s2", content="文本2", source="t2.txt", position=(0, 3))
    ]
    service.import_engine.import_file.return_value = mock_segments
    
    result = service.import_file("test2.txt")
    
    assert len(result) == 1
    # Verify session was updated and saved
    service.session_repo.save.assert_called_once()
