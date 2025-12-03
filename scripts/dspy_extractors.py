"""
Centralized DSPy Extractors Module

This module provides all DSPy extractors with centralized LLM configuration,
eliminating duplicate configuration code across the codebase.

Usage:
    from dspy_extractors import Extractors
    
    # Get pre-configured extractors
    table_extractor = Extractors.table_column()
    result = table_extractor(sql_query=sql, chart_metadata=meta)
"""
import logging
from typing import Optional, Dict, Any
from functools import lru_cache
import threading

import dspy

from llm_config import configure_dspy, get_lm

logger = logging.getLogger(__name__)

# Import signatures from llm_extractor
# Note: This creates a slight circular dependency that we handle carefully
_signatures_loaded = False
_signatures_lock = threading.Lock()

# Signature classes - will be populated on first use
TableColumnExtractor = None
SourceTableColumnExtractor = None
TableMetadataExtractor = None
ColumnMetadataExtractor = None
JoiningConditionExtractor = None
FilterConditionsExtractor = None
TermDefinitionExtractor = None


def _load_signatures() -> None:
    """Load signature classes from llm_extractor module."""
    global _signatures_loaded
    global TableColumnExtractor, SourceTableColumnExtractor, TableMetadataExtractor
    global ColumnMetadataExtractor, JoiningConditionExtractor, FilterConditionsExtractor
    global TermDefinitionExtractor
    
    if _signatures_loaded:
        return
    
    with _signatures_lock:
        if _signatures_loaded:
            return
        
        from llm_extractor import (
            TableColumnExtractor as _TableColumnExtractor,
            SourceTableColumnExtractor as _SourceTableColumnExtractor,
            TableMetadataExtractor as _TableMetadataExtractor,
            ColumnMetadataExtractor as _ColumnMetadataExtractor,
            JoiningConditionExtractor as _JoiningConditionExtractor,
            FilterConditionsExtractor as _FilterConditionsExtractor,
            TermDefinitionExtractor as _TermDefinitionExtractor,
        )
        
        TableColumnExtractor = _TableColumnExtractor
        SourceTableColumnExtractor = _SourceTableColumnExtractor
        TableMetadataExtractor = _TableMetadataExtractor
        ColumnMetadataExtractor = _ColumnMetadataExtractor
        JoiningConditionExtractor = _JoiningConditionExtractor
        FilterConditionsExtractor = _FilterConditionsExtractor
        TermDefinitionExtractor = _TermDefinitionExtractor
        
        _signatures_loaded = True


class Extractors:
    """
    Factory class for creating DSPy extractors with centralized configuration.
    
    All extractors use the same LLM configuration from llm_config module.
    Extractors are cached for reuse within the same process.
    """
    
    _cache: Dict[str, Any] = {}
    _lock = threading.Lock()
    
    @classmethod
    def _get_or_create(cls, name: str, signature_class: type) -> dspy.Module:
        """Get cached extractor or create new one."""
        if name not in cls._cache:
            with cls._lock:
                if name not in cls._cache:
                    configure_dspy()
                    cls._cache[name] = dspy.ChainOfThought(signature_class)
                    logger.debug(f"Created extractor: {name}")
        return cls._cache[name]
    
    @classmethod
    def table_column(cls) -> dspy.Module:
        """Get TableColumnExtractor for extracting tables and columns from SQL."""
        _load_signatures()
        return cls._get_or_create("table_column", TableColumnExtractor)
    
    @classmethod
    def source_table_column(cls) -> dspy.Module:
        """Get SourceTableColumnExtractor for extracting source tables and derived columns."""
        _load_signatures()
        return cls._get_or_create("source_table_column", SourceTableColumnExtractor)
    
    @classmethod
    def table_metadata(cls) -> dspy.Module:
        """Get TableMetadataExtractor for extracting table descriptions."""
        _load_signatures()
        return cls._get_or_create("table_metadata", TableMetadataExtractor)
    
    @classmethod
    def column_metadata(cls) -> dspy.Module:
        """Get ColumnMetadataExtractor for extracting column descriptions."""
        _load_signatures()
        return cls._get_or_create("column_metadata", ColumnMetadataExtractor)
    
    @classmethod
    def joining_condition(cls) -> dspy.Module:
        """Get JoiningConditionExtractor for extracting join conditions."""
        _load_signatures()
        return cls._get_or_create("joining_condition", JoiningConditionExtractor)
    
    @classmethod
    def filter_conditions(cls) -> dspy.Module:
        """Get FilterConditionsExtractor for extracting filter conditions."""
        _load_signatures()
        return cls._get_or_create("filter_conditions", FilterConditionsExtractor)
    
    @classmethod
    def term_definition(cls) -> dspy.Module:
        """Get TermDefinitionExtractor for extracting term definitions."""
        _load_signatures()
        return cls._get_or_create("term_definition", TermDefinitionExtractor)
    
    @classmethod
    def clear_cache(cls) -> None:
        """Clear all cached extractors. Useful for testing."""
        with cls._lock:
            cls._cache.clear()


# Convenience functions for backwards compatibility
def get_table_column_extractor() -> dspy.Module:
    """Get pre-configured TableColumnExtractor."""
    return Extractors.table_column()


def get_source_table_column_extractor() -> dspy.Module:
    """Get pre-configured SourceTableColumnExtractor."""
    return Extractors.source_table_column()


def get_table_metadata_extractor() -> dspy.Module:
    """Get pre-configured TableMetadataExtractor."""
    return Extractors.table_metadata()


def get_column_metadata_extractor() -> dspy.Module:
    """Get pre-configured ColumnMetadataExtractor."""
    return Extractors.column_metadata()


def get_joining_condition_extractor() -> dspy.Module:
    """Get pre-configured JoiningConditionExtractor."""
    return Extractors.joining_condition()


def get_filter_conditions_extractor() -> dspy.Module:
    """Get pre-configured FilterConditionsExtractor."""
    return Extractors.filter_conditions()


def get_term_definition_extractor() -> dspy.Module:
    """Get pre-configured TermDefinitionExtractor."""
    return Extractors.term_definition()

