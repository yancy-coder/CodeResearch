"""Coding service - coordinates coding engines and repositories."""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from CodeEngine.ir.code_ir import TextSegment, CodeUnit
from repositories.code_repository import CodeRepository, CodeEntity
from repositories.category_repository import CategoryRepository
from repositories.session_repository import SessionRepository


@dataclass
class CodingResult:
    """编码结果"""
    success: bool
    codes: List[CodeUnit]
    categories: List[Any]
    core_category: Optional[Any]
    message: str = ""


class CodingService:
    """编码服务 - 协调各 Engine 完成编码工作流"""
    
    def __init__(
        self,
        code_repo: CodeRepository,
        category_repo: CategoryRepository,
        session_repo: SessionRepository,
        engines: Dict[str, Any]
    ):
        self.code_repo = code_repo
        self.category_repo = category_repo
        self.session_repo = session_repo
        self.engines = engines
    
    def run_open_coding(
        self,
        segments: List[TextSegment],
        config: Optional[Dict] = None
    ) -> CodingResult:
        """运行开放编码"""
        open_coding = self.engines.get('open_coding')
        if not open_coding:
            return CodingResult(False, [], [], None, "Open coding engine not available")
        
        # 配置引擎
        if config:
            from CodeEngine.open_coding.agent import OpenCodingConfig
            open_coding.config = OpenCodingConfig(**config)
        
        # 批量编码
        result = open_coding.batch_code(segments)
        
        # 保存代码
        for code in result.get('approved_codes', []):
            entity = CodeEntity(
                id=code.id,
                label=code.code_label,
                definition=code.code_definition,
                level="open",
                created_by=code.created_by.value
            )
            self.code_repo.save(entity)
        
        return CodingResult(
            success=True,
            codes=result.get('approved_codes', []),
            categories=[],
            core_category=None,
            message=f"Generated {len(result.get('approved_codes', []))} codes"
        )
    
    def run_axial_coding(self, codes: List[CodeUnit]) -> CodingResult:
        """运行轴心编码"""
        axial_coding = self.engines.get('axial_coding')
        if not axial_coding:
            return CodingResult(False, codes, [], None, "Axial coding engine not available")
        
        categories = axial_coding.categorize_codes(codes)
        
        # 保存类属
        for cat in categories:
            from repositories.category_repository import CategoryEntity
            entity = CategoryEntity(
                id=cat.id,
                name=cat.name,
                definition=cat.definition
            )
            self.category_repo.save(entity)
        
        return CodingResult(
            success=True,
            codes=codes,
            categories=categories,
            core_category=None,
            message=f"Generated {len(categories)} categories"
        )
    
    def run_selective_coding(self, categories: List[Any]) -> CodingResult:
        """运行选择性编码"""
        selective_coding = self.engines.get('selective_coding')
        if not selective_coding:
            return CodingResult(False, [], categories, None, "Selective coding engine not available")
        
        core_category = selective_coding.identify_core_category(categories)
        
        return CodingResult(
            success=True,
            codes=[],
            categories=categories,
            core_category=core_category,
            message=f"Core category: {core_category.name if core_category else 'None'}"
        )
    
    def run_full_pipeline(
        self,
        segments: List[TextSegment],
        config: Optional[Dict] = None
    ) -> CodingResult:
        """运行完整编码工作流"""
        # Step 1: 开放编码
        result1 = self.run_open_coding(segments, config)
        if not result1.success:
            return result1
        
        # Step 2: 轴心编码
        result2 = self.run_axial_coding(result1.codes)
        if not result2.success:
            return CodingResult(
                success=True,
                codes=result1.codes,
                categories=[],
                core_category=None,
                message="Open coding done, axial coding failed"
            )
        
        # Step 3: 选择性编码
        result3 = self.run_selective_coding(result2.categories)
        
        return CodingResult(
            success=True,
            codes=result1.codes,
            categories=result2.categories,
            core_category=result3.core_category,
            message="Full pipeline completed"
        )
    
    def get_coding_status(self) -> Dict[str, Any]:
        """获取当前编码状态"""
        codes = self.code_repo.list()
        categories = self.category_repo.list()
        
        return {
            "total_codes": len(codes),
            "total_categories": len(categories),
            "open_codes": len([c for c in codes if c.level == "open"]),
            "axial_codes": len([c for c in codes if c.level == "axial"])
        }
