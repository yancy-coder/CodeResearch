"""
国际化 (i18n) 支持
支持中文和英文界面
"""
from typing import Dict
from enum import Enum


class Language(Enum):
    """支持的语言"""
    ZH = "zh"      # 简体中文
    EN = "en"      # 英文


class I18n:
    """国际化管理器"""
    
    def __init__(self, lang: Language = Language.ZH):
        self.lang = lang
        self._translations = self._load_translations()
    
    def _load_translations(self) -> Dict[str, Dict[str, str]]:
        """加载翻译字符串"""
        return {
            Language.ZH.value: {
                # 通用
                "app_name": "CoderResearch",
                "app_description": "定性研究智能编码系统",
                "confirm": "确认",
                "cancel": "取消",
                "save": "保存",
                "delete": "删除",
                "edit": "编辑",
                "back": "返回",
                "next": "下一步",
                "finish": "完成",
                "loading": "加载中...",
                "success": "成功",
                "error": "错误",
                "warning": "警告",
                "info": "提示",
                
                # 菜单
                "menu_import": "导入数据",
                "menu_open_code": "开放编码",
                "menu_axial_code": "轴心编码",
                "menu_selective_code": "选择性编码",
                "menu_visualize": "可视化",
                "menu_memo": "备忘录",
                "menu_report": "报告",
                "menu_discuss": "讨论",
                
                # 编码相关
                "coding_progress": "编码进度",
                "coding_complete": "编码完成",
                "code_label": "代码标签",
                "code_definition": "代码定义",
                "code_confidence": "置信度",
                "ai_suggestion": "AI 建议",
                "human_review": "人工审核",
                "approve": "批准",
                "reject": "拒绝",
                "modify": "修改",
                "review_comment": "审核意见",
                
                # 审核状态
                "status_pending": "待审核",
                "status_approved": "已通过",
                "status_rejected": "已拒绝",
                "status_modified": "已修改",
                
                # 饱和度
                "saturation_check": "饱和度检查",
                "saturation_high": "高",
                "saturation_medium": "中",
                "saturation_low": "低",
                "coverage": "覆盖率",
                
                # 导出
                "export_format": "导出格式",
                "export_markdown": "Markdown",
                "export_docx": "Word",
                "export_nvivo": "NVivo",
                "export_atlasti": "Atlas.ti",
                
                # 错误信息
                "error_no_data": "请先导入数据",
                "error_no_codes": "请先完成编码",
                "error_api_failed": "API 调用失败，已切换到模拟模式",
                "error_json_parse": "JSON 解析失败",
                
                # LLM 相关
                "llm_health_check": "LLM 健康检查",
                "llm_available": "可用",
                "llm_unavailable": "不可用",
                "llm_fallback": "已降级到",
            },
            Language.EN.value: {
                # General
                "app_name": "CoderResearch",
                "app_description": "Qualitative Research Smart Coding System",
                "confirm": "Confirm",
                "cancel": "Cancel",
                "save": "Save",
                "delete": "Delete",
                "edit": "Edit",
                "back": "Back",
                "next": "Next",
                "finish": "Finish",
                "loading": "Loading...",
                "success": "Success",
                "error": "Error",
                "warning": "Warning",
                "info": "Info",
                
                # Menu
                "menu_import": "Import Data",
                "menu_open_code": "Open Coding",
                "menu_axial_code": "Axial Coding",
                "menu_selective_code": "Selective Coding",
                "menu_visualize": "Visualize",
                "menu_memo": "Memo",
                "menu_report": "Report",
                "menu_discuss": "Discuss",
                
                # Coding
                "coding_progress": "Coding Progress",
                "coding_complete": "Coding Complete",
                "code_label": "Code Label",
                "code_definition": "Code Definition",
                "code_confidence": "Confidence",
                "ai_suggestion": "AI Suggestion",
                "human_review": "Human Review",
                "approve": "Approve",
                "reject": "Reject",
                "modify": "Modify",
                "review_comment": "Review Comment",
                
                # Review Status
                "status_pending": "Pending",
                "status_approved": "Approved",
                "status_rejected": "Rejected",
                "status_modified": "Modified",
                
                # Saturation
                "saturation_check": "Saturation Check",
                "saturation_high": "High",
                "saturation_medium": "Medium",
                "saturation_low": "Low",
                "coverage": "Coverage",
                
                # Export
                "export_format": "Export Format",
                "export_markdown": "Markdown",
                "export_docx": "Word",
                "export_nvivo": "NVivo",
                "export_atlasti": "Atlas.ti",
                
                # Error Messages
                "error_no_data": "Please import data first",
                "error_no_codes": "Please complete coding first",
                "error_api_failed": "API call failed, switched to mock mode",
                "error_json_parse": "JSON parse failed",
                
                # LLM
                "llm_health_check": "LLM Health Check",
                "llm_available": "Available",
                "llm_unavailable": "Unavailable",
                "llm_fallback": "Fallback to",
            }
        }
    
    def set_language(self, lang: Language):
        """设置语言"""
        self.lang = lang
    
    def t(self, key: str, **kwargs) -> str:
        """
        获取翻译字符串
        
        Args:
            key: 翻译键
            **kwargs: 格式化参数
            
        Returns:
            翻译后的字符串
        """
        translations = self._translations.get(self.lang.value, {})
        text = translations.get(key, key)
        
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError:
                pass
        
        return text
    
    def __call__(self, key: str, **kwargs) -> str:
        """快捷调用"""
        return self.t(key, **kwargs)


# 全局 i18n 实例
i18n = I18n()


def set_language(lang: Language):
    """设置全局语言"""
    i18n.set_language(lang)


def t(key: str, **kwargs) -> str:
    """全局翻译函数"""
    return i18n.t(key, **kwargs)
