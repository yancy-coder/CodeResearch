"""
CoderResearch 全局配置
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """应用配置类"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8"
    )
    
    # LLM 配置
    openai_api_key: str = ""
    openai_base_url: str = "https://api.openai.com/v1"
    default_model: str = "gpt-4"
    
    # 数据库
    database_url: str = "sqlite:///./coderresearch.db"
    
    # 文件路径
    data_dir: str = "./data"
    upload_dir: str = "./uploads"
    output_dir: str = "./outputs"
    
    # 日志
    log_level: str = "INFO"
    
    # 协作配置
    enable_ai_peer_review: bool = True
    enable_devil_advocate: bool = True
    consensus_threshold: float = 0.8


# 全局配置实例
settings = Settings()
