"""Import service - wraps import engine and session management."""
from typing import List
from pathlib import Path

from CodeEngine.ir.code_ir import TextSegment


class ImportService:
    """导入服务 - 封装导入逻辑"""
    
    def __init__(self, import_engine, session_repo):
        self.import_engine = import_engine
        self.session_repo = session_repo
    
    def import_file(
        self,
        file_path: str,
        segment_type: str = "paragraph",
        anonymize: bool = True
    ) -> List[TextSegment]:
        """导入文件并返回文本片段"""
        from ImportEngine.agent import ImportConfig
        
        config = ImportConfig(anonymize=anonymize)
        self.import_engine.config = config
        
        segments = self.import_engine.import_file(file_path, segment_type)
        
        # 保存到会话
        self._save_to_session(segments, file_path)
        
        return segments
    
    def _save_to_session(self, segments: List[TextSegment], source_file: str):
        """保存导入结果到会话"""
        from repositories.session_repository import SessionEntity
        
        session = self.session_repo.get("default")
        if not session:
            session = SessionEntity(id="default")
        
        session.data['segments'] = [
            {
                'id': s.id,
                'content': s.content,
                'source': s.source,
                'position': s.position
            }
            for s in segments
        ]
        session.data['source_file'] = source_file
        
        self.session_repo.save(session)
