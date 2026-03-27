"""Backward compatibility layer for deprecated access patterns.

This module provides deprecated global instance accessors for code
that hasn't been migrated to the new service/repository pattern.
"""
import warnings


def get_legacy_import_engine():
    """Get ImportEngine (deprecated, use services/import_service.py)."""
    warnings.warn(
        "Direct global engine access is deprecated. Use services.import_service instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from ImportEngine.agent import ImportEngine
    return ImportEngine()


def get_legacy_open_coding_agent():
    """Get OpenCodingAgent (deprecated, use services/coding_service.py)."""
    warnings.warn(
        "Direct global Agent access is deprecated. Use services.coding_service instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from CodeEngine.open_coding.agent import OpenCodingAgent
    return OpenCodingAgent()


def get_legacy_axial_coding_agent():
    """Get AxialCodingAgent (deprecated, use services/coding_service.py)."""
    warnings.warn(
        "Direct global Agent access is deprecated. Use services.coding_service instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from CodeEngine.axial_coding.agent import AxialCodingAgent
    return AxialCodingAgent()


def get_legacy_selective_coding_agent():
    """Get SelectiveCodingAgent (deprecated, use services/coding_service.py)."""
    warnings.warn(
        "Direct global Agent access is deprecated. Use services.coding_service instead.",
        DeprecationWarning,
        stacklevel=2
    )
    from CodeEngine.selective_coding.agent import SelectiveCodingAgent
    return SelectiveCodingAgent()


def get_legacy_db():
    """Get CodebookDB (deprecated, use repositories)."""
    warnings.warn(
        "Direct DB access is deprecated. Use repositories from repositories/.",
        DeprecationWarning,
        stacklevel=2
    )
    from CodebookDB.db import CodebookDB
    return CodebookDB()
