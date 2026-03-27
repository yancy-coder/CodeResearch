"""Tests for category repository."""
import pytest
from repositories.category_repository import CategoryRepository, CategoryEntity
from CodebookDB.db import CodebookDB


@pytest.fixture
def repository():
    db = CodebookDB("sqlite:///:memory:")
    return CategoryRepository(db)


def test_save_and_get_category(repository):
    cat = CategoryEntity(
        id="cat-001",
        name="用户体验",
        definition="关于用户体验的类属"
    )
    repository.save(cat)
    
    retrieved = repository.get("cat-001")
    assert retrieved.name == "用户体验"
    assert retrieved.definition == "关于用户体验的类属"


def test_hierarchical_categories(repository):
    """测试层级类属"""
    parent = CategoryEntity(id="p1", name="父类属")
    child = CategoryEntity(id="c1", name="子类属", parent_id="p1")
    
    repository.save(parent)
    repository.save(child)
    
    children = repository.get_children("p1")
    assert len(children) == 1
    assert children[0].name == "子类属"


def test_filter_by_parent_id(repository):
    """测试按 parent_id 过滤"""
    repository.save(CategoryEntity(id="root1", name="Root 1"))
    repository.save(CategoryEntity(id="root2", name="Root 2"))
    repository.save(CategoryEntity(id="child1", name="Child", parent_id="root1"))
    
    root_categories = repository.list(parent_id=None)
    assert len(root_categories) == 2
    
    children = repository.list(parent_id="root1")
    assert len(children) == 1
    assert children[0].name == "Child"


def test_get_nonexistent_category(repository):
    result = repository.get("nonexistent")
    assert result is None


def test_delete_category(repository):
    cat = CategoryEntity(id="del-001", name="To Delete")
    repository.save(cat)
    
    result = repository.delete("del-001")
    assert result is True
    assert repository.get("del-001") is None


def test_delete_nonexistent_category(repository):
    result = repository.delete("nonexistent")
    assert result is False
