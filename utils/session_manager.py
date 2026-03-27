"""
会话管理器 - 替代 pickle 的数据库存储
"""
import json
from typing import Dict, Optional, List, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from datetime import datetime
from sqlalchemy import create_engine, Column, String, DateTime, Text, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
import json

from config import settings

Base = declarative_base()


class SessionModel(Base):
    """会话数据模型"""
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, default="default")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    data = Column(JSON, default=dict)


class SessionManager:
    """会话管理器
    
    将会话数据持久化到 SQLite 数据库，替代原来的 pickle 方案
    """
    
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or settings.database_url
        self.engine = create_engine(self.db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
    
    def save_session(self, data: Dict, session_id: str = "default") -> bool:
        """保存会话数据
        
        Args:
            data: 会话数据字典
            session_id: 会话 ID（默认 default）
            
        Returns:
            是否成功
        """
        session = self.Session()
        try:
            # 将对象转换为可序列化格式
            serialized_data = self._serialize_data(data)
            
            # 转换为 JSON 字符串再转回，确保所有类型都可序列化
            json_str = json.dumps(serialized_data, ensure_ascii=False)
            clean_data = json.loads(json_str)
            
            # 检查是否已存在
            existing = session.query(SessionModel).filter_by(id=session_id).first()
            
            if existing:
                existing.data = clean_data
                existing.updated_at = datetime.now()
            else:
                new_session = SessionModel(
                    id=session_id,
                    data=clean_data
                )
                session.add(new_session)
            
            session.commit()
            return True
            
        except Exception as e:
            print(f"保存会话失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def load_session(self, session_id: str = "default") -> Optional[Dict]:
        """加载会话数据
        
        Args:
            session_id: 会话 ID
            
        Returns:
            会话数据字典，不存在则返回 None
        """
        session = self.Session()
        try:
            record = session.query(SessionModel).filter_by(id=session_id).first()
            
            if record and record.data:
                return self._deserialize_data(record.data)
            return None
            
        except Exception as e:
            print(f"加载会话失败: {e}")
            return None
        finally:
            session.close()
    
    def clear_session(self, session_id: str = "default") -> bool:
        """清除会话数据"""
        session = self.Session()
        try:
            record = session.query(SessionModel).filter_by(id=session_id).first()
            if record:
                session.delete(record)
                session.commit()
                return True
            return False
        except Exception as e:
            print(f"清除会话失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def list_sessions(self) -> List[Dict]:
        """列出所有会话"""
        session = self.Session()
        try:
            records = session.query(SessionModel).order_by(
                SessionModel.updated_at.desc()
            ).all()
            
            return [
                {
                    "id": r.id,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "updated_at": r.updated_at.isoformat() if r.updated_at else None,
                    "data_keys": list(r.data.keys()) if r.data else []
                }
                for r in records
            ]
        finally:
            session.close()
    
    def _serialize_data(self, data: Dict) -> Dict:
        """序列化数据（处理特殊类型）"""
        result = {}
        
        for key, value in data.items():
            result[key] = self._serialize_value(value)
        
        return result
    
    def _serialize_value(self, value):
        """序列化单个值"""
        if value is None:
            return None
        elif isinstance(value, (str, int, float, bool)):
            return value
        elif isinstance(value, list):
            # 递归处理列表中的每个元素
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, dict):
            # 递归处理字典中的每个值
            return {k: self._serialize_value(v) for k, v in value.items()}
        elif isinstance(value, tuple):
            # 元组转为列表
            return [self._serialize_value(item) for item in value]
        elif hasattr(value, '__dataclass_fields__'):
            # 处理 dataclass - 使用自定义转换
            data = {}
            for k, v in value.__dict__.items():
                data[k] = self._serialize_value(v)
            return {
                "__type__": "dataclass",
                "__class__": value.__class__.__name__,
                "data": data
            }
        elif isinstance(value, datetime):
            return value.isoformat()
        else:
            # 其他类型转为字符串
            return str(value)
    
    def _deserialize_data(self, data: Dict) -> Dict:
        """反序列化数据"""
        # 延迟导入以避免循环依赖
        from CodeEngine.ir.code_ir import TextSegment, CodeUnit, Category
        from CodeEngine.selective_coding.agent import StoryLine
        from datetime import datetime
        
        result = {}
        
        for key, value in data.items():
            if value is None:
                result[key] = None
            elif isinstance(value, dict) and value.get("__type__") == "dataclass":
                # 还原 dataclass
                class_name = value.get("__class__")
                class_data = value.get("data", {})
                
                # 根据类名还原
                if class_name == "TextSegment":
                    result[key] = TextSegment(**class_data)
                elif class_name == "CodeUnit":
                    # 需要特殊处理 text_segment 嵌套
                    if "text_segment" in class_data and isinstance(class_data["text_segment"], dict):
                        class_data["text_segment"] = TextSegment(**class_data["text_segment"])
                    result[key] = CodeUnit(**class_data)
                elif class_name == "Category":
                    result[key] = Category(**class_data)
                elif class_name == "StoryLine":
                    result[key] = StoryLine(**class_data)
                else:
                    result[key] = class_data
            elif isinstance(value, list):
                # 处理列表
                result[key] = [
                    self._deserialize_data({"item": item}).get("item") if isinstance(item, dict) and item.get("__type__") == "dataclass"
                    else item
                    for item in value
                ]
            else:
                result[key] = value
        
        return result
    
    def backup_session(self, backup_path: str, session_id: str = "default") -> bool:
        """备份会话到 JSON 文件"""
        data = self.load_session(session_id)
        if data is None:
            return False
        
        try:
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"备份失败: {e}")
            return False
    
    def restore_session(self, backup_path: str, session_id: str = "default") -> bool:
        """从 JSON 文件恢复会话"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return self.save_session(data, session_id)
        except Exception as e:
            print(f"恢复失败: {e}")
            return False
