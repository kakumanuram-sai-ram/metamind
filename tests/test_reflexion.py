"""
Tests for reflexion-based metadata validation.

Run with: pytest tests/test_reflexion.py -v
"""
import os
import sys
import pytest

# Add scripts directory to path
_scripts_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_scripts_dir, 'scripts'))

from reflexion_extractor import (
    should_skip_reflexion,
    detect_score_degradation,
    normalize_score,
    generate_reflection_prompt,
    JudgeResult
)
from context_storage import ChartContextStore, EntityContext


class TestReflexionSkipping:
    """Tests for should_skip_reflexion function."""
    
    def test_skip_reflexion_when_all_high_confidence(self):
        """Should skip reflexion when all scores >= 0.85."""
        scores = {
            'tables': 0.90,
            'columns': 0.88,
            'joins': 0.86,
            'filters': 0.92,
            'definitions': 0.87
        }
        assert should_skip_reflexion(scores) == True
    
    def test_reflexion_needed_when_low_confidence(self):
        """Should require reflexion when any score < 0.85."""
        scores = {
            'tables': 0.75,  # Below threshold
            'columns': 0.88,
            'joins': 0.90,
            'filters': 0.85,
            'definitions': 0.91
        }
        assert should_skip_reflexion(scores) == False
    
    def test_skip_reflexion_at_threshold(self):
        """Should skip reflexion when scores exactly at threshold (0.85)."""
        scores = {
            'tables': 0.85,
            'columns': 0.85,
            'joins': 0.85,
            'filters': 0.85,
            'definitions': 0.85
        }
        assert should_skip_reflexion(scores) == True
    
    def test_empty_scores(self):
        """Should not skip reflexion with empty scores."""
        assert should_skip_reflexion({}) == False
    
    def test_partial_low_scores(self):
        """Should require reflexion when only some scores are low."""
        scores = {
            'tables': 0.50,
            'columns': 0.95,
            'joins': 0.99
        }
        assert should_skip_reflexion(scores) == False


class TestScoreDegradation:
    """Tests for detect_score_degradation function."""
    
    def test_detect_degradation(self):
        """Should detect when scores get worse."""
        history = [
            {'iteration': 0, 'scores': {'tables': 0.82, 'columns': 0.80}},
            {'iteration': 1, 'scores': {'tables': 0.78, 'columns': 0.75}}  # Worse!
        ]
        assert detect_score_degradation(history) == True
    
    def test_no_degradation_when_improving(self):
        """Should not detect degradation when scores improve."""
        history = [
            {'iteration': 0, 'scores': {'tables': 0.75, 'columns': 0.70}},
            {'iteration': 1, 'scores': {'tables': 0.85, 'columns': 0.82}}  # Better!
        ]
        assert detect_score_degradation(history) == False
    
    def test_no_degradation_single_iteration(self):
        """Should not detect degradation with single iteration."""
        history = [
            {'iteration': 0, 'scores': {'tables': 0.75}}
        ]
        assert detect_score_degradation(history) == False
    
    def test_no_degradation_empty_history(self):
        """Should not detect degradation with empty history."""
        assert detect_score_degradation([]) == False
    
    def test_no_degradation_same_scores(self):
        """Should not detect degradation when scores stay the same."""
        history = [
            {'iteration': 0, 'scores': {'tables': 0.82}},
            {'iteration': 1, 'scores': {'tables': 0.82}}  # Same
        ]
        assert detect_score_degradation(history) == False


class TestScoreNormalization:
    """Tests for normalize_score function."""
    
    def test_normalize_zero(self):
        """Should normalize 0 to 0.0."""
        assert normalize_score(0) == 0.0
    
    def test_normalize_hundred(self):
        """Should normalize 100 to 1.0."""
        assert normalize_score(100) == 1.0
    
    def test_normalize_middle(self):
        """Should normalize 85 to 0.85."""
        assert normalize_score(85) == 0.85
    
    def test_normalize_over_hundred(self):
        """Should cap at 1.0 for values over 100."""
        assert normalize_score(150) == 1.0
    
    def test_normalize_negative(self):
        """Should floor at 0.0 for negative values."""
        assert normalize_score(-10) == 0.0
    
    def test_normalize_float(self):
        """Should handle float inputs."""
        assert normalize_score(75.5) == 0.755


class TestReflectionPromptGeneration:
    """Tests for generate_reflection_prompt function."""
    
    def test_prompt_contains_issues(self):
        """Should include issues in reflection prompt."""
        chart_json = {
            'chart_name': 'Test Chart',
            'sql_query': 'SELECT * FROM test_table',
            'metrics': []
        }
        judge_result = JudgeResult(
            confidence=0.70,
            quality_issues='Missing table descriptions',
            recommendations='Add detailed descriptions',
            missing_items=['table_a', 'table_b']
        )
        
        prompt = generate_reflection_prompt(
            'tables', chart_json, [], judge_result
        )
        
        assert 'Missing table descriptions' in prompt
        assert 'Add detailed descriptions' in prompt
        assert 'table_a' in prompt or 'table_b' in prompt
    
    def test_prompt_contains_chart_context(self):
        """Should include chart context in reflection prompt."""
        chart_json = {
            'chart_name': 'Revenue Analysis',
            'sql_query': 'SELECT sum(amount) FROM transactions',
            'metrics': [{'label': 'Total Revenue'}]
        }
        judge_result = JudgeResult(
            confidence=0.70,
            quality_issues='Incomplete extraction',
            recommendations='Include all columns'
        )
        
        prompt = generate_reflection_prompt(
            'columns', chart_json, [], judge_result
        )
        
        assert 'Revenue Analysis' in prompt
        assert 'transactions' in prompt


class TestContextStorage:
    """Tests for ChartContextStore class."""
    
    def test_add_and_get_context(self):
        """Should add and retrieve contexts correctly."""
        store = ChartContextStore()
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=123,
            chart_name='Test Chart',
            metadata={'description': 'Test description'},
            confidence=0.90,
            iteration_count=1
        )
        
        contexts = store.get_contexts('tables', 'hive.cdo.transactions')
        
        assert len(contexts) == 1
        assert contexts[0]['chart_id'] == 123
        assert contexts[0]['confidence'] == 0.90
    
    def test_multiple_contexts_same_entity(self):
        """Should store multiple contexts for same entity."""
        store = ChartContextStore()
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=123,
            chart_name='Chart 1',
            metadata={'description': 'Desc 1'},
            confidence=0.85,
            iteration_count=1
        )
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=456,
            chart_name='Chart 2',
            metadata={'description': 'Desc 2'},
            confidence=0.88,
            iteration_count=2
        )
        
        contexts = store.get_contexts('tables', 'hive.cdo.transactions')
        
        assert len(contexts) == 2
        assert contexts[0]['chart_id'] == 123
        assert contexts[1]['chart_id'] == 456
    
    def test_auto_lock_high_confidence(self):
        """Should auto-lock entity with 3+ contexts and high avg confidence."""
        store = ChartContextStore()
        
        for i in range(3):
            store.add_context(
                entity_type='tables',
                entity_key='hive.cdo.transactions',
                chart_id=100 + i,
                chart_name=f'Chart {i}',
                metadata={'description': f'Desc {i}'},
                confidence=0.90,  # High confidence
                iteration_count=1
            )
        
        assert store.is_locked('tables', 'hive.cdo.transactions') == True
    
    def test_no_auto_lock_low_confidence(self):
        """Should not auto-lock entity with low avg confidence."""
        store = ChartContextStore()
        
        for i in range(3):
            store.add_context(
                entity_type='tables',
                entity_key='hive.cdo.transactions',
                chart_id=100 + i,
                chart_name=f'Chart {i}',
                metadata={'description': f'Desc {i}'},
                confidence=0.70,  # Low confidence
                iteration_count=1
            )
        
        assert store.is_locked('tables', 'hive.cdo.transactions') == False
    
    def test_get_all_entities(self):
        """Should return all entity keys for a type."""
        store = ChartContextStore()
        
        store.add_context('tables', 'table_a', 1, 'C1', {}, 0.9, 1)
        store.add_context('tables', 'table_b', 2, 'C2', {}, 0.85, 1)
        store.add_context('columns', 'col_a', 3, 'C3', {}, 0.88, 1)
        
        table_keys = store.get_all_entities('tables')
        
        assert 'table_a' in table_keys
        assert 'table_b' in table_keys
        assert len(table_keys) == 2
    
    def test_clear_store(self):
        """Should clear all stored contexts."""
        store = ChartContextStore()
        
        store.add_context('tables', 'table_a', 1, 'C1', {}, 0.9, 1)
        store.clear()
        
        assert store.get_all_entities('tables') == []


class TestConflictDetection:
    """Tests for conflict detection in context storage."""
    
    def test_detect_refresh_frequency_conflict(self):
        """Should detect conflict when refresh frequencies differ."""
        store = ChartContextStore()
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=1,
            chart_name='Chart 1',
            metadata={'refresh_frequency': 'daily'},
            confidence=0.9,
            iteration_count=1
        )
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=2,
            chart_name='Chart 2',
            metadata={'refresh_frequency': 'hourly'},  # Different!
            confidence=0.85,
            iteration_count=1
        )
        
        conflict = store.detect_conflicts('tables', 'hive.cdo.transactions')
        
        assert conflict is not None
        assert 'refresh_frequency' in conflict['conflicting_fields']
        assert conflict['severity'] == 'MEDIUM'
    
    def test_no_conflict_same_values(self):
        """Should not detect conflict when values are the same."""
        store = ChartContextStore()
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=1,
            chart_name='Chart 1',
            metadata={'refresh_frequency': 'daily'},
            confidence=0.9,
            iteration_count=1
        )
        
        store.add_context(
            entity_type='tables',
            entity_key='hive.cdo.transactions',
            chart_id=2,
            chart_name='Chart 2',
            metadata={'refresh_frequency': 'daily'},  # Same
            confidence=0.85,
            iteration_count=1
        )
        
        conflict = store.detect_conflicts('tables', 'hive.cdo.transactions')
        
        assert conflict is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

