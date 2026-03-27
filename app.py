"""
CoderResearch 主应用入口
重构版：分层架构（CLI → Service → Engine → Repository）
"""
from cli.commands import app

if __name__ == "__main__":
    app()
