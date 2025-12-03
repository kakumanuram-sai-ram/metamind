"""
Context Storage Module for Per-Chart Metadata Contexts

This module provides thread-safe storage for per-chart metadata contexts before merging.
It enables tracking of which chart contributed which metadata, supporting:
1. Append-only writes (no overwrites)
2. Locking high-confidence entities
3. Conflict detection across charts
4. Provenance tracking (which chart contributed what)

Storage Location: extracted_meta/{dashboard_id}/contexts.json
"""

import os
import json
import threading
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class EntityContext:
    """Single chart's context for an entity (table/column/join/filter/definition)."""
    chart_id: int
    chart_name: str
    metadata: Dict  # Type-specific metadata
    confidence: float
    iteration_count: int


class ChartContextStore:
    """
    Thread-safe storage for per-chart metadata contexts.
    
    Stores all metadata contexts before merging, allowing:
    1. Append-only writes (no overwrites)
    2. Locking high-confidence entities (3+ charts with avg confidence >= 0.85)
    3. Conflict detection across charts
    4. Provenance tracking (which chart contributed what)
    
    Data Structure:
    {
        "tables": {
            "hive.cdo.fact_upi_transactions": {
                "contexts": [
                    {
                        "chart_id": 2646,
                        "chart_name": "Overall SR",
                        "metadata": {
                            "table_description": "UPI P2P transfer transactions...",
                            "refresh_frequency": "daily",
                            "vertical": "payments"
                        },
                        "confidence": 0.90,
                        "iteration_count": 1
                    },
                    ...
                ],
                "locked": false
            }
        },
        "columns": { ... },
        "joins": { ... },
        "filters": { ... },
        "definitions": { ... }
    }
    """
    
    def __init__(self):
        """Initialize the context store with empty structure."""
        self._store: Dict[str, Dict[str, Dict]] = {
            'tables': {},
            'columns': {},
            'joins': {},
            'filters': {},
            'definitions': {}
        }
        self._lock = threading.Lock()
        self._dashboard_ids: List[int] = []
    
    def add_context(
        self,
        entity_type: str,
        entity_key: str,
        chart_id: int,
        chart_name: str,
        metadata: Dict,
        confidence: float,
        iteration_count: int = 1
    ) -> None:
        """
        Add per-chart context (append-only, never overwrites existing contexts).
        
        Args:
            entity_type: One of 'tables', 'columns', 'joins', 'filters', 'definitions'
            entity_key: Unique key for the entity
                - For tables: table_name (e.g., 'hive.cdo.fact_upi_transactions')
                - For columns: table_name.column_name (e.g., 'hive.cdo.fact.txn_id')
                - For joins: table1|table2 (sorted alphabetically)
                - For filters: chart_id (since filters are per-chart)
                - For definitions: term_name
            chart_id: Chart ID that extracted this
            chart_name: Chart name for provenance
            metadata: Type-specific metadata dict
            confidence: Confidence score (0-1)
            iteration_count: Number of reflexion iterations used
        """
        if entity_type not in self._store:
            raise ValueError(f"Invalid entity_type: {entity_type}")
        
        with self._lock:
            if entity_key not in self._store[entity_type]:
                self._store[entity_type][entity_key] = {
                    'contexts': [],
                    'locked': False
                }
            
            # Create context object
            context = EntityContext(
                chart_id=chart_id,
                chart_name=chart_name,
                metadata=metadata,
                confidence=confidence,
                iteration_count=iteration_count
            )
            
            # Append (never overwrite)
            self._store[entity_type][entity_key]['contexts'].append(asdict(context))
            
            # Check and auto-lock if high confidence consensus reached
            self._check_and_lock(entity_type, entity_key)
    
    def _check_and_lock(self, entity_type: str, entity_key: str) -> None:
        """
        Lock entity if high confidence consensus reached.
        
        Auto-lock condition: 3+ charts with average confidence >= 0.85
        
        Note: Must be called within lock context.
        """
        entity = self._store[entity_type][entity_key]
        contexts = entity['contexts']
        
        if len(contexts) >= 3:
            avg_confidence = sum(c['confidence'] for c in contexts) / len(contexts)
            if avg_confidence >= 0.85:
                entity['locked'] = True
                logger.debug(f"Auto-locked {entity_type}/{entity_key} (avg confidence: {avg_confidence:.2f})")
    
    def get_contexts(self, entity_type: str, entity_key: str) -> List[Dict]:
        """
        Get all contexts for an entity.
        
        Args:
            entity_type: One of 'tables', 'columns', 'joins', 'filters', 'definitions'
            entity_key: Unique key for the entity
            
        Returns:
            List of context dicts, empty list if not found
        """
        with self._lock:
            if entity_key in self._store.get(entity_type, {}):
                return self._store[entity_type][entity_key]['contexts'].copy()
            return []
    
    def is_locked(self, entity_type: str, entity_key: str) -> bool:
        """
        Check if entity is locked (high confidence, skip reflexion).
        
        Args:
            entity_type: One of 'tables', 'columns', 'joins', 'filters', 'definitions'
            entity_key: Unique key for the entity
            
        Returns:
            True if locked, False otherwise
        """
        with self._lock:
            if entity_key in self._store.get(entity_type, {}):
                return self._store[entity_type][entity_key].get('locked', False)
            return False
    
    def get_all_entities(self, entity_type: str) -> List[str]:
        """
        Get all entity keys of a type.
        
        Args:
            entity_type: One of 'tables', 'columns', 'joins', 'filters', 'definitions'
            
        Returns:
            List of entity keys
        """
        with self._lock:
            return list(self._store.get(entity_type, {}).keys())
    
    def get_all_contexts_for_type(self, entity_type: str) -> Dict[str, List[Dict]]:
        """
        Get all contexts for a metadata type.
        
        Args:
            entity_type: One of 'tables', 'columns', 'joins', 'filters', 'definitions'
            
        Returns:
            Dict mapping entity_key to list of contexts
        """
        with self._lock:
            result = {}
            for entity_key, entity_data in self._store.get(entity_type, {}).items():
                result[entity_key] = entity_data['contexts'].copy()
            return result
    
    def get_store_summary(self) -> Dict[str, int]:
        """
        Get summary counts of stored contexts.
        
        Returns:
            Dict with counts per entity type
        """
        with self._lock:
            return {
                entity_type: len(entities)
                for entity_type, entities in self._store.items()
            }
    
    def clear(self) -> None:
        """Clear all stored contexts."""
        with self._lock:
            self._store = {
                'tables': {},
                'columns': {},
                'joins': {},
                'filters': {},
                'definitions': {}
            }
            self._dashboard_ids = []
    
    def save_to_disk(self, dashboard_id: int, output_dir: str = "extracted_meta") -> str:
        """
        Save contexts to extracted_meta/{dashboard_id}/contexts.json.
        
        Args:
            dashboard_id: Dashboard ID
            output_dir: Base output directory
            
        Returns:
            Path to saved file
        """
        output_path = f"{output_dir}/{dashboard_id}/contexts.json"
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with self._lock:
            save_data = {
                'dashboard_id': dashboard_id,
                'store': self._store,
                'summary': {
                    entity_type: {
                        'entity_count': len(entities),
                        'total_contexts': sum(len(e['contexts']) for e in entities.values()),
                        'locked_count': sum(1 for e in entities.values() if e.get('locked', False))
                    }
                    for entity_type, entities in self._store.items()
                }
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Context store saved to {output_path}")
        return output_path
    
    def load_from_disk(self, dashboard_id: int, input_dir: str = "extracted_meta") -> bool:
        """
        Load contexts from disk and merge into current store.
        
        Used for multi-dashboard merging where contexts from multiple
        dashboards need to be combined.
        
        Args:
            dashboard_id: Dashboard ID to load
            input_dir: Base input directory
            
        Returns:
            True if loaded successfully, False if file not found
        """
        input_path = f"{input_dir}/{dashboard_id}/contexts.json"
        
        if not os.path.exists(input_path):
            logger.warning(f"Context file not found: {input_path}")
            return False
        
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            
            loaded_store = loaded.get('store', {})
            
            with self._lock:
                # Track dashboard IDs
                if dashboard_id not in self._dashboard_ids:
                    self._dashboard_ids.append(dashboard_id)
                
                # Merge loaded contexts into existing store
                for entity_type in loaded_store:
                    if entity_type not in self._store:
                        self._store[entity_type] = {}
                    
                    for entity_key in loaded_store[entity_type]:
                        if entity_key not in self._store[entity_type]:
                            self._store[entity_type][entity_key] = {
                                'contexts': [],
                                'locked': False
                            }
                        
                        # Append contexts (avoid duplicates based on chart_id)
                        existing_chart_ids = {
                            c['chart_id'] 
                            for c in self._store[entity_type][entity_key]['contexts']
                        }
                        
                        for context in loaded_store[entity_type][entity_key].get('contexts', []):
                            if context['chart_id'] not in existing_chart_ids:
                                self._store[entity_type][entity_key]['contexts'].append(context)
                        
                        # Recheck lock status after merge
                        self._check_and_lock(entity_type, entity_key)
            
            logger.info(f"Loaded contexts from {input_path} for dashboard {dashboard_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error loading contexts from {input_path}: {e}")
            return False
    
    def get_dashboard_ids(self) -> List[int]:
        """Get list of dashboard IDs that have been loaded."""
        with self._lock:
            return self._dashboard_ids.copy()
    
    def detect_conflicts(self, entity_type: str, entity_key: str) -> Optional[Dict]:
        """
        Detect conflicts in metadata for an entity across charts.
        
        A conflict is detected when different charts provide contradictory
        values for the same field (e.g., different refresh_frequency).
        
        Args:
            entity_type: One of 'tables', 'columns', 'joins', 'filters', 'definitions'
            entity_key: Unique key for the entity
            
        Returns:
            Dict with conflict details if conflicts found, None otherwise
            {
                'entity_type': 'tables',
                'entity_key': 'hive.cdo.fact_upi',
                'conflicting_fields': ['refresh_frequency'],
                'field_values': {
                    'refresh_frequency': {
                        'daily': [chart_id_1, chart_id_2],
                        'hourly': [chart_id_3]
                    }
                },
                'severity': 'MEDIUM'
            }
        """
        contexts = self.get_contexts(entity_type, entity_key)
        
        if len(contexts) < 2:
            return None
        
        # Fields to check for conflicts by entity type
        conflict_fields = {
            'tables': ['refresh_frequency', 'vertical', 'partition_column'],
            'columns': ['variable_type', 'required_flag'],
            'joins': ['joining_condition'],
            'filters': [],  # Filters are expected to be different
            'definitions': ['type']
        }
        
        fields_to_check = conflict_fields.get(entity_type, [])
        if not fields_to_check:
            return None
        
        conflicting_fields = []
        field_values = {}
        
        for field in fields_to_check:
            values_by_chart = {}
            
            for context in contexts:
                metadata = context.get('metadata', {})
                value = metadata.get(field, '')
                
                # Skip empty values
                if not value or str(value).strip() == '':
                    continue
                
                # Normalize value for comparison
                normalized_value = str(value).strip().lower()
                
                if normalized_value not in values_by_chart:
                    values_by_chart[normalized_value] = []
                values_by_chart[normalized_value].append(context['chart_id'])
            
            # Conflict if multiple different non-empty values
            if len(values_by_chart) > 1:
                conflicting_fields.append(field)
                field_values[field] = values_by_chart
        
        if not conflicting_fields:
            return None
        
        # Assess severity
        high_severity_fields = {'variable_type', 'required_flag', 'joining_condition'}
        has_high_severity = any(f in high_severity_fields for f in conflicting_fields)
        severity = 'HIGH' if has_high_severity else 'MEDIUM'
        
        return {
            'entity_type': entity_type,
            'entity_key': entity_key,
            'conflicting_fields': conflicting_fields,
            'field_values': field_values,
            'severity': severity,
            'affected_charts': list(set(
                chart_id 
                for field_data in field_values.values() 
                for chart_ids in field_data.values() 
                for chart_id in chart_ids
            ))
        }
    
    def detect_all_conflicts(self) -> List[Dict]:
        """
        Detect conflicts across all entities in the store.
        
        Returns:
            List of conflict dicts for all detected conflicts
        """
        all_conflicts = []
        
        for entity_type in self._store:
            for entity_key in self.get_all_entities(entity_type):
                conflict = self.detect_conflicts(entity_type, entity_key)
                if conflict:
                    all_conflicts.append(conflict)
        
        # Sort by severity (HIGH first)
        severity_order = {'HIGH': 0, 'MEDIUM': 1, 'LOW': 2}
        all_conflicts.sort(key=lambda c: severity_order.get(c.get('severity', 'LOW'), 2))
        
        return all_conflicts


# Global context store instance with thread-safe initialization
_global_context_store: Optional[ChartContextStore] = None
_context_store_lock = threading.Lock()


def get_context_store() -> ChartContextStore:
    """
    Get or create global context store instance (thread-safe).
    
    Returns:
        ChartContextStore singleton instance
    """
    global _global_context_store
    
    if _global_context_store is None:
        with _context_store_lock:
            # Double-check pattern
            if _global_context_store is None:
                _global_context_store = ChartContextStore()
    
    return _global_context_store


def reset_context_store() -> ChartContextStore:
    """
    Reset and return a fresh context store instance.
    
    Use this when starting a new extraction to clear previous state.
    
    Returns:
        Fresh ChartContextStore instance
    """
    global _global_context_store
    
    with _context_store_lock:
        _global_context_store = ChartContextStore()
    
    return _global_context_store

