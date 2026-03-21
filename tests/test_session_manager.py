"""
测试会话管理器
"""
import pytest
import json
import os
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils.session_manager import SessionManager, SessionModel, Base
from CodeEngine.ir.code_ir import TextSegment, CodeUnit, CodeSource


class TestSessionManager:
    """测试会话管理器"""
    
    @pytest.fixture
    def db_url(self):
        """测试数据库 URL"""
        return "sqlite:///:memory:"
    
    @pytest.fixture
    def manager(self, db_url):
        """创建会话管理器"""
        return SessionManager(db_url)
    
    @pytest.fixture
    def sample_data(self):
        """测试数据"""
        return {
            "segments": [
                TextSegment(
                    id="S001",
                    content="测试文本",
                    source="test.txt",
                    position=(0, 10)
                )
            ],
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    def test_save_and_load_session(self, manager, sample_data):
        """测试保存和加载会话"""
        # 保存
        result = manager.save_session(sample_data, "test_session")
        assert result == True
        
        # 加载
        loaded = manager.load_session("test_session")
        assert loaded is not None
        assert "segments" in loaded
        assert len(loaded["segments"]) == 1
        assert loaded["segments"][0].id == "S001"
    
    def test_load_nonexistent_session(self, manager):
        """测试加载不存在的会话"""
        loaded = manager.load_session("nonexistent")
        assert loaded is None
    
    def test_update_existing_session(self, manager, sample_data):
        """测试更新已存在的会话"""
        # 首次保存
        manager.save_session(sample_data, "update_test")
        
        # 修改数据
        sample_data["metadata"]["version"] = "2.0"
        
        # 再次保存
        manager.save_session(sample_data, "update_test")
        
        # 验证更新
        loaded = manager.load_session("update_test")
        assert loaded["metadata"]["version"] == "2.0"
    
    def test_clear_session(self, manager, sample_data):
        """测试清除会话"""
        manager.save_session(sample_data, "clear_test")
        
        # 清除
        result = manager.clear_session("clear_test")
        assert result == True
        
        # 验证已删除
        loaded = manager.load_session("clear_test")
        assert loaded is None
        
        # 清除不存在的会话
        result = manager.clear_session("nonexistent")
        assert result == False
    
    def test_list_sessions(self, manager):
        """测试列会话"""
        # 创建多个会话
        manager.save_session({"data": "session1"}, "session_1")
        manager.save_session({"data": "session2"}, "session_2")
        manager.save_session({"data": "session3"}, "session_3")
        
        sessions = manager.list_sessions()
        
        assert len(sessions) == 3
        # 应该按更新时间倒序
        assert sessions[0]["id"] == "session_3"
    
    def test_backup_and_restore(self, manager, sample_data, tmp_path):
        """测试备份和恢复"""
        # 保存会话
        manager.save_session(sample_data, "backup_test")
        
        # 备份
        backup_path = str(tmp_path / "backup.json")
        result = manager.backup_session(backup_path, "backup_test")
        assert result == True
        assert os.path.exists(backup_path)
        
        # 清除原会话
        manager.clear_session("backup_test")
        
        # 恢复
        result = manager.restore_session(backup_path, "restored_session")
        assert result == True
        
        # 验证恢复的数据
        loaded = manager.load_session("restored_session")
        assert loaded is not None
        assert "segments" in loaded


class TestSerialization:
    """测试序列化/反序列化"""
    
    @pytest.fixture
    def manager(self):
        return SessionManager("sqlite:///:memory:")
    
    def test_serialize_simple_types(self, manager):
        """测试简单类型序列化"""
        data = {
            "string": "test",
            "integer": 42,
            "float": 3.14,
            "boolean": True,
            "null": None,
            "list": [1, 2, 3],
            "dict": {"a": 1}
        }
        
        serialized = manager._serialize_data(data)
        
        assert serialized["string"] == "test"
        assert serialized["integer"] == 42
        assert serialized["float"] == 3.14
        assert serialized["boolean"] == True
        assert serialized["null"] is None
        assert serialized["list"] == [1, 2, 3]
        assert serialized["dict"] == {"a": 1}
    
    def test_serialize_text_segment(self, manager):
        """测试 TextSegment 序列化"""
        segment = TextSegment(
            id="S001",
            content="测试",
            source="test.txt",
            position=(0, 5)
        )
        
        data = {"segment": segment}
        serialized = manager._serialize_data(data)
        
        assert serialized["segment"]["__type__"] == "dataclass"
        assert serialized["segment"]["__class__"] == "TextSegment"
        assert serialized["segment"]["data"]["id"] == "S001"
    
    def test_serialize_code_unit(self, manager):
        """测试 CodeUnit 序列化"""
        segment = TextSegment(
            id="S001",
            content="测试",
            source="test.txt",
            position=(0, 5)
        )
        code = CodeUnit(
            id="C001",
            text_segment=segment,
            code_label="测试代码",
            code_definition="定义",
            created_by=CodeSource.AI,
            confidence=0.8
        )
        
        data = {"code": code}
        serialized = manager._serialize_data(data)
        
        assert serialized["code"]["__type__"] == "dataclass"
        assert serialized["code"]["__class__"] == "CodeUnit"
    
    def test_deserialize_text_segment(self, manager):
        """测试 TextSegment 反序列化"""
        serialized = {
            "__type__": "dataclass",
            "__class__": "TextSegment",
            "data": {
                "id": "S001",
                "content": "测试内容",
                "source": "test.txt",
                "position": [0, 10],
                "metadata": {},
                "created_at": datetime.now().isoformat()
            }
        }
        
        data = {"segment": serialized}
        deserialized = manager._deserialize_data(data)
        
        segment = deserialized["segment"]
        assert isinstance(segment, TextSegment)
        assert segment.id == "S001"
        assert segment.content == "测试内容"
    
    def test_round_trip(self, manager):
        """测试完整的序列化-反序列化循环"""
        original = {
            "segments": [
                TextSegment(
                    id="S001",
                    content="测试",
                    source="test.txt",
                    position=(0, 5)
                )
            ],
            "metadata": {"version": "1.0"}
        }
        
        # 序列化
        serialized = manager._serialize_data(original)
        
        # 反序列化
        deserialized = manager._deserialize_data(serialized)
        
        # 验证
        assert len(deserialized["segments"]) == 1
        assert deserialized["segments"][0].id == "S001"
        assert deserialized["metadata"]["version"] == "1.0"


class TestSessionErrorHandling:
    """测试错误处理"""
    
    def test_save_with_invalid_data(self):
        """测试保存无效数据"""
        manager = SessionManager("sqlite:///:memory:")
        
        # 包含不可序列化对象的数据
        class Unserializable:
            pass
        
        data = {"invalid": Unserializable()}
        
        # 应该转换为字符串而不是失败
        result = manager.save_session(data, "error_test")
        assert result == True


class TestDefaultSession:
    """测试默认会话"""
    
    def test_default_session_id(self):
        """测试默认会话 ID"""
        manager = SessionManager("sqlite:///:memory:")
        
        data = {"test": "data"}
        manager.save_session(data)  # 不指定 ID
        
        loaded = manager.load_session("default")
        assert loaded is not None
        assert loaded["test"] == "data"
