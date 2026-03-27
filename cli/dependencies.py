"""CLI dependency management."""
from functools import lru_cache

from config import settings
from CodebookDB.db import CodebookDB
from repositories.code_repository import CodeRepository
from repositories.category_repository import CategoryRepository
from repositories.session_repository import SessionRepository

from ImportEngine.agent import ImportEngine
from CodeEngine.open_coding.agent import OpenCodingAgent
from CodeEngine.axial_coding.agent import AxialCodingAgent
from CodeEngine.selective_coding.agent import SelectiveCodingAgent

from services.coding_service import CodingService
from services.import_service import ImportService


@lru_cache()
def get_db() -> CodebookDB:
    return CodebookDB()


@lru_cache()
def get_code_repository() -> CodeRepository:
    return CodeRepository(get_db())


@lru_cache()
def get_category_repository() -> CategoryRepository:
    return CategoryRepository(get_db())


@lru_cache()
def get_session_repository() -> SessionRepository:
    return SessionRepository(get_db())


def get_coding_service() -> CodingService:
    engines = {
        'open_coding': OpenCodingAgent(),
        'axial_coding': AxialCodingAgent(),
        'selective_coding': SelectiveCodingAgent()
    }
    return CodingService(
        code_repo=get_code_repository(),
        category_repo=get_category_repository(),
        session_repo=get_session_repository(),
        engines=engines
    )


def get_import_service() -> ImportService:
    return ImportService(
        import_engine=ImportEngine(),
        session_repo=get_session_repository()
    )
