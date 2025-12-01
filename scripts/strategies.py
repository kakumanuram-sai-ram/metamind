"""
Strategy Pattern - Pluggable algorithms

This module provides different strategies for metadata extraction,
allowing easy switching between LLM-based and rule-based approaches.
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import logging

try:
    from models import ChartInfo
except ImportError:
    from scripts.models import ChartInfo

logger = logging.getLogger(__name__)


class IExtractionStrategy(ABC):
    """
    Abstract strategy for metadata extraction.
    
    This allows different extraction implementations (LLM, rule-based, hybrid)
    to be used interchangeably.
    """
    
    @abstractmethod
    def extract_tables_columns(self, chart: ChartInfo) -> Dict[str, Any]:
        """
        Extract tables and columns from chart SQL query.
        
        Args:
            chart: Chart information including SQL query
        
        Returns:
            Dictionary with extracted tables and columns
        """
        pass
    
    @abstractmethod
    def get_strategy_name(self) -> str:
        """Get the name of this strategy"""
        pass


class LLMExtractionStrategy(IExtractionStrategy):
    """LLM-based extraction using DSPy"""
    
    def __init__(self, api_key: str, model: str, base_url: str):
        """
        Initialize LLM extraction strategy.
        
        Args:
            api_key: LLM API key
            model: Model name
            base_url: API base URL
        """
        self.api_key = api_key
        self.model = model
        self.base_url = base_url
    
    def extract_tables_columns(self, chart: ChartInfo) -> Dict[str, Any]:
        """Extract using LLM"""
        try:
            from llm_extractor import extract_table_column_mapping_llm
            
            # Convert chart to dict format expected by extractor
            chart_dict = chart.to_dict()
            dashboard_info = {
                'charts': [chart_dict]
            }
            
            result = extract_table_column_mapping_llm(
                dashboard_info=dashboard_info,
                api_key=self.api_key,
                model=self.model,
                base_url=self.base_url
            )
            
            return result if result else {}
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            raise
    
    def get_strategy_name(self) -> str:
        return "llm"


class RuleBasedExtractionStrategy(IExtractionStrategy):
    """Rule-based SQL parsing strategy"""
    
    def extract_tables_columns(self, chart: ChartInfo) -> Dict[str, Any]:
        """Extract using SQL parsing rules"""
        try:
            from sql_parser import extract_table_column_mapping
            
            # Convert chart to dict format expected by parser
            chart_dict = chart.to_dict()
            dashboard_info = {
                'charts': [chart_dict]
            }
            
            result = extract_table_column_mapping(
                dashboard_info=dashboard_info,
                trino_columns={}
            )
            
            return result if result else []
        except Exception as e:
            logger.error(f"Rule-based extraction failed: {e}")
            raise
    
    def get_strategy_name(self) -> str:
        return "rule_based"


class HybridExtractionStrategy(IExtractionStrategy):
    """Hybrid strategy - tries LLM first, falls back to rules"""
    
    def __init__(
        self,
        llm_strategy: LLMExtractionStrategy,
        rule_strategy: RuleBasedExtractionStrategy
    ):
        """
        Initialize hybrid strategy.
        
        Args:
            llm_strategy: LLM extraction strategy
            rule_strategy: Rule-based extraction strategy
        """
        self.llm_strategy = llm_strategy
        self.rule_strategy = rule_strategy
    
    def extract_tables_columns(self, chart: ChartInfo) -> Dict[str, Any]:
        """Try LLM first, fall back to rules on failure"""
        try:
            logger.debug(f"Trying LLM extraction for chart {chart.chart_id}")
            result = self.llm_strategy.extract_tables_columns(chart)
            logger.debug(f"LLM extraction succeeded for chart {chart.chart_id}")
            return result
        except Exception as e:
            logger.warning(
                f"LLM extraction failed for chart {chart.chart_id}: {e}. "
                f"Falling back to rule-based extraction"
            )
            try:
                result = self.rule_strategy.extract_tables_columns(chart)
                logger.debug(f"Rule-based extraction succeeded for chart {chart.chart_id}")
                return result
            except Exception as fallback_error:
                logger.error(
                    f"Both LLM and rule-based extraction failed "
                    f"for chart {chart.chart_id}: {fallback_error}"
                )
                return {}
    
    def get_strategy_name(self) -> str:
        return "hybrid"


def create_extraction_strategy(
    strategy_type: str,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    base_url: Optional[str] = None
) -> IExtractionStrategy:
    """
    Factory function to create extraction strategy.
    
    Args:
        strategy_type: Type of strategy ('llm', 'rule_based', 'hybrid')
        api_key: LLM API key (required for 'llm' and 'hybrid')
        model: LLM model (required for 'llm' and 'hybrid')
        base_url: LLM base URL (required for 'llm' and 'hybrid')
    
    Returns:
        Configured extraction strategy
    """
    if strategy_type == "llm":
        if not all([api_key, model, base_url]):
            raise ValueError("LLM strategy requires api_key, model, and base_url")
        return LLMExtractionStrategy(api_key, model, base_url)
    
    elif strategy_type == "rule_based":
        return RuleBasedExtractionStrategy()
    
    elif strategy_type == "hybrid":
        if not all([api_key, model, base_url]):
            raise ValueError("Hybrid strategy requires api_key, model, and base_url")
        llm_strat = LLMExtractionStrategy(api_key, model, base_url)
        rule_strat = RuleBasedExtractionStrategy()
        return HybridExtractionStrategy(llm_strat, rule_strat)
    
    else:
        raise ValueError(f"Unknown strategy type: {strategy_type}")

