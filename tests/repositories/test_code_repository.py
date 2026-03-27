"""Tests for code repository."""
import pytest
from repositories.code_repository import CodeRepository, CodeEntity
from CodebookDB.db import CodebookDB


@pytest.fixture
def db():
    return CodebookDB("sqlite:///:memory:")


@pytest.fixture
def repository(db):
    return CodeRepository(db)


@pytest.fixture
def sample_code():
    return CodeEntity(
        id="test-001",
        label="测试代码",
        definition="这是一个测试代码定义",
        level="open",
        created_by="human"
    )


def test_save_code(repository, sample_code):
    code_id = repository.save(sample_code)
    assert code_id == "test-001"


def test_get_code(repository, sample_code):
    repository.save(sample_code)
    code = repository.get("test-001")
    assert code is not None
    assert code.label == "测试代码"


def test_get_nonexistent_code(repository):
    code = repository.get("nonexistent")
    assert code is None


def test_list_codes(repository):
    for i in range(3):
        code = CodeEntity(
            id=f"code-{i}",
            label=f"代码{i}",
            definition=f"定义{i}",
            level="open"
        )
        repository.save(code)
    
    codes = repository.list()
    assert len(codes) == 3


def test_filter_by_level(repository):
    repository.save(CodeEntity(id="c1", label="A", level="open"))
    repository.save(CodeEntity(id="c2", label="B", level="axial"))
    
    open_codes = repository.list(level="open")
    assert len(open_codes) == 1
    assert open_codes[0].label == "A"


def test_delete_code(repository, sample_code):
    repository.save(sample_code)
    result = repository.delete("test-001")
    assert result is True
    assert repository.get("test-001") is None


def test_delete_nonexistent_code(repository):
    result = repository.delete("nonexistent")
    assert result is False
