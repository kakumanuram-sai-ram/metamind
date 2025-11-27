"""
Instruction Set Generator Module (LLM-Powered)

This module generates comprehensive instruction sets for SQL-writing agents using LLM
based on:
- Business vertical and sub-vertical context
- Available metadata (tables, columns, joins, filters, definitions)

The LLM analyzes the actual metadata and generates domain-specific, intelligent
guidance for accurate SQL query generation.
"""

import os
import json
import dspy
from typing import Dict, List, Optional, Any
from datetime import datetime
from config import LLM_API_KEY, LLM_MODEL, LLM_BASE_URL


# Vertical context information for LLM enrichment
# 'short_name' is used for tag matching in Superset dashboards
VERTICAL_CONTEXT = {
    'upi': {
        'name': 'UPI (Unified Payments Interface)',
        'short_name': 'UPI',  # Used for tag matching
        'description': 'Payment transactions through UPI platform including P2P and P2M payments',
        'domain_context': 'Financial payments, transaction processing, banking integrations',
        'sub_verticals': {
            'UPI Growth': ['upi', 'upi growth', 'upi-growth'],
            'User Growth': ['user growth', 'user-growth', 'upi user'],
        },
        'tags': ['upi', 'upi-growth', 'upi growth', 'unified payments'],
    },
    'merchant': {
        'name': 'Merchant Business',
        'short_name': 'Merchant',  # Used for tag matching
        'description': 'Merchant acquisition, onboarding, and transaction processing',
        'domain_context': 'B2B payments, merchant services, POS/QR/EDC deployments',
        'sub_verticals': {
            'QR / SB': ['qr', 'sb', 'soundbox', 'qr code', 'merchant qr'],
            'EDC': ['edc', 'pos', 'terminal', 'edc terminal'],
            'All Offline Merchant': ['offline merchant', 'offline', 'merchant offline'],
        },
        'tags': ['merchant', 'merchant-business', 'b2b'],
    },
    'lending': {
        'name': 'Lending Business',
        'short_name': 'Lending',  # Used for tag matching
        'description': 'Loan products including MCA and Personal Loans',
        'domain_context': 'Credit products, loan lifecycle, collections, risk management',
        'sub_verticals': {
            'MCA': ['mca', 'merchant cash advance', 'cash advance'],
            'PL': ['pl', 'personal loan', 'personal loans'],
        },
        'tags': ['lending', 'loans', 'credit'],
    },
    'travel': {
        'name': 'Travel Business',
        'short_name': 'Travel',  # Used for tag matching
        'description': 'Travel booking services including flights, trains, and buses',
        'domain_context': 'Online travel agency, booking systems, inventory management',
        'sub_verticals': {
            'Flights': ['flights', 'flight', 'air travel', 'airline'],
            'Trains': ['trains', 'train', 'irctc', 'railway'],
            'Bus': ['bus', 'buses', 'bus travel'],
        },
        'tags': ['travel', 'booking', 'ota'],
    },
    'recharges': {
        'name': 'Recharges & Utilities',
        'short_name': 'Recharges',  # Used for tag matching
        'description': 'Mobile recharges and utility bill payments',
        'domain_context': 'BBPS payments, telecom recharges, utility services',
        'sub_verticals': {
            'Electricity': ['electricity', 'electric', 'power'],
            'Broadband': ['broadband', 'internet', 'wifi'],
            'Mobile': ['mobile', 'recharge', 'prepaid', 'postpaid'],
        },
        'tags': ['recharges', 'utilities', 'bbps', 'bill payments'],
    },
}


def get_tags_for_vertical(vertical: str, sub_vertical: str = None) -> List[str]:
    """
    Get tags to search for based on vertical and sub-vertical selection.
    Priority: Use sub_vertical if provided, otherwise use vertical short_name
    
    Example: 
      - vertical='upi', sub_vertical='UPI Growth' -> tags = ['UPI Growth']
      - vertical='upi', sub_vertical=None -> tags = ['UPI']
    
    Args:
        vertical: Vertical ID (e.g., 'upi', 'merchant')
        sub_vertical: Sub-vertical name (e.g., 'UPI Growth', 'QR / SB')
        
    Returns:
        List of tag strings (single tag based on most specific selection)
    """
    tags = []
    
    # If sub-vertical is selected, use it as the tag
    if sub_vertical:
        tags.append(sub_vertical)
    # Otherwise, use the vertical short name
    elif vertical in VERTICAL_CONTEXT:
        vertical_info = VERTICAL_CONTEXT[vertical]
        short_name = vertical_info.get('short_name', '')
        if short_name:
            tags.append(short_name)
    
    return tags


def get_verticals_with_sub_verticals() -> List[Dict[str, Any]]:
    """
    Get list of all verticals with their sub-verticals.
    
    Returns:
        List of vertical dictionaries with id, name, description, and sub_verticals
    """
    return [
        {
            'id': v_id,
            'name': v_info['name'],
            'description': v_info['description'],
            'sub_verticals': list(v_info.get('sub_verticals', {}).keys()),
            'tags': v_info.get('tags', []),
        }
        for v_id, v_info in VERTICAL_CONTEXT.items()
    ]


class InstructionSetSignature(dspy.Signature):
    """
    Generate comprehensive SQL query writing instructions based on metadata knowledge base.
    
    SYSTEM PROMPT: SQL Agent Instruction Set Generator
    
    ## Objective
    Analyze the provided metadata (tables, columns, joins, filters, definitions) and generate
    a comprehensive instruction set that will guide an AI agent in writing accurate SQL queries.
    
    ## Instructions Structure
    The output should include:
    1. **Domain Understanding**: Key business concepts and terminology
    2. **Data Model Overview**: How tables relate to each other, key entities
    3. **Query Best Practices**: SQL patterns, performance tips, common pitfalls
    4. **Metric Calculations**: Standard formulas and aggregation patterns
    5. **Filter Guidelines**: Required filters, date handling, partition columns
    6. **Example Patterns**: Reusable SQL templates for common questions
    
    ## Quality Requirements
    - Be specific to the actual metadata provided
    - Reference actual table and column names from the metadata
    - Include actual join conditions from the joining_conditions
    - Incorporate business definitions from the definitions
    - Make instructions actionable and concrete
    """
    
    vertical_context: str = dspy.InputField(desc="Business vertical and sub-vertical context")
    table_metadata: str = dspy.InputField(desc="JSON string with table names, descriptions, refresh frequencies")
    column_metadata: str = dspy.InputField(desc="JSON string with column names, types, and descriptions")
    joining_conditions: str = dspy.InputField(desc="JSON string with table join patterns and conditions")
    filter_conditions: str = dspy.InputField(desc="Text content with standard filter conditions from dashboards")
    definitions: str = dspy.InputField(desc="JSON string with business term definitions and metrics")
    
    domain_understanding: str = dspy.OutputField(desc="2-3 paragraphs explaining key business concepts, entities, and terminology specific to this domain and data model")
    data_model_overview: str = dspy.OutputField(desc="Description of the data model: key tables, their purposes, relationships, and how they should be joined")
    query_best_practices: str = dspy.OutputField(desc="Numbered list of SQL best practices including: partition filters, aggregation patterns, date handling, performance tips specific to these tables")
    metric_calculations: str = dspy.OutputField(desc="List of standard metric formulas and calculations based on the definitions provided, with SQL examples")
    filter_guidelines: str = dspy.OutputField(desc="Specific guidance on required filters, date ranges, and conditions that should be applied based on the filter_conditions")
    example_patterns: str = dspy.OutputField(desc="3-5 reusable SQL query templates using actual table/column names from the metadata for common analytical questions")


class ExampleQueryGenerator(dspy.Signature):
    """
    Generate example SQL queries based on metadata for common analytical questions.
    """
    
    table_metadata: str = dspy.InputField(desc="JSON string with available tables and their descriptions")
    column_metadata: str = dspy.InputField(desc="JSON string with columns and their types")
    joining_conditions: str = dspy.InputField(desc="JSON string with join patterns")
    vertical_context: str = dspy.InputField(desc="Business vertical context")
    
    example_queries: str = dspy.OutputField(desc="JSON array of 5 example queries. Each should have: description (what the query answers), query (complete SQL using actual table/column names), explanation (why this pattern is useful)")


class InstructionSetGenerator:
    """LLM-powered instruction set generator using DSPy."""
    
    def __init__(self, api_key: str = None, model: str = None, base_url: str = None):
        """
        Initialize the instruction set generator.
        
        Args:
            api_key: LLM API key (default: from config)
            model: Model name (default: from config)
            base_url: API base URL (default: from config)
        """
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY") or LLM_API_KEY
        self.model = model or LLM_MODEL
        self.base_url = base_url or LLM_BASE_URL
        
        # Configure DSPy
        self.lm = dspy.LM(
            model=self.model,
            api_key=self.api_key,
            api_provider="anthropic"
        )
        dspy.configure(lm=self.lm)
        
        # Create extractors
        self.instruction_extractor = dspy.ChainOfThought(InstructionSetSignature)
        self.example_generator = dspy.ChainOfThought(ExampleQueryGenerator)
    
    def generate(
        self,
        vertical: Optional[str] = None,
        sub_vertical: Optional[str] = None,
        kb_dir: str = "extracted_meta/knowledge_base"
    ) -> Dict[str, Any]:
        """
        Generate instruction set using LLM based on metadata.
        
        Args:
            vertical: Business vertical ID
            sub_vertical: Sub-vertical name
            kb_dir: Knowledge base directory
            
        Returns:
            Complete instruction set dictionary
        """
        print("📚 Loading metadata from knowledge base...")
        metadata = self._load_metadata(kb_dir)
        
        # Build vertical context
        vertical_info = VERTICAL_CONTEXT.get(vertical, {})
        vertical_context = f"""
Business Vertical: {vertical_info.get('name', 'General Analytics')}
Description: {vertical_info.get('description', 'Cross-vertical analytics and reporting')}
Domain Context: {vertical_info.get('domain_context', 'General business analytics')}
Sub-Vertical: {sub_vertical or 'Not specified'}
"""
        
        print("🤖 Generating instructions using LLM...")
        
        try:
            # Generate main instructions
            result = self.instruction_extractor(
                vertical_context=vertical_context,
                table_metadata=json.dumps(metadata['tables'][:30], indent=2),  # Limit for context
                column_metadata=json.dumps(metadata['columns'][:100], indent=2),
                joining_conditions=json.dumps(metadata['joins'][:20], indent=2),
                filter_conditions=metadata['filters'][:3000],  # Limit text length
                definitions=json.dumps(metadata['definitions'][:30], indent=2)
            )
            
            print("📝 Generating example queries...")
            
            # Generate example queries
            examples_result = self.example_generator(
                table_metadata=json.dumps(metadata['tables'][:20], indent=2),
                column_metadata=json.dumps(metadata['columns'][:50], indent=2),
                joining_conditions=json.dumps(metadata['joins'][:15], indent=2),
                vertical_context=vertical_context
            )
            
            # Parse example queries
            try:
                example_queries = json.loads(examples_result.example_queries)
            except json.JSONDecodeError:
                # Try to extract JSON from the response
                example_queries = self._extract_json_array(examples_result.example_queries)
            
            # Build instruction set
            instruction_set = {
                'generated_at': datetime.now().isoformat(),
                'version': '2.0',
                'generation_method': 'LLM (Claude)',
                'purpose': 'SQL Query Generation Agent Instructions',
                'context': {
                    'vertical': {
                        'id': vertical or 'general',
                        'name': vertical_info.get('name', 'General Analytics'),
                        'description': vertical_info.get('description', 'Cross-vertical analytics'),
                        'domain_context': vertical_info.get('domain_context', ''),
                    },
                    'sub_vertical': sub_vertical,
                },
                'instructions': [
                    {
                        'category': 'Domain Understanding',
                        'priority': 'HIGH',
                        'content': result.domain_understanding
                    },
                    {
                        'category': 'Data Model Overview',
                        'priority': 'HIGH',
                        'content': result.data_model_overview
                    },
                    {
                        'category': 'Query Best Practices',
                        'priority': 'HIGH',
                        'content': result.query_best_practices
                    },
                    {
                        'category': 'Metric Calculations',
                        'priority': 'MEDIUM',
                        'content': result.metric_calculations
                    },
                    {
                        'category': 'Filter Guidelines',
                        'priority': 'MEDIUM',
                        'content': result.filter_guidelines
                    },
                    {
                        'category': 'Example SQL Patterns',
                        'priority': 'LOW',
                        'content': result.example_patterns
                    },
                ],
                'example_queries': example_queries,
                'metadata_summary': {
                    'tables_count': len(metadata['tables']),
                    'columns_count': len(metadata['columns']),
                    'joins_count': len(metadata['joins']),
                    'definitions_count': len(metadata['definitions']),
                    'tables': [t.get('table_name', '') for t in metadata['tables'][:10]],
                },
            }
            
            print("✅ Instruction set generated successfully!")
            return instruction_set
            
        except Exception as e:
            print(f"❌ Error generating instructions with LLM: {str(e)}")
            # Return fallback with error info
            return self._generate_fallback(vertical, sub_vertical, metadata, str(e))
    
    def _load_metadata(self, kb_dir: str) -> Dict[str, Any]:
        """Load metadata from knowledge base files."""
        metadata = {
            'tables': [],
            'columns': [],
            'joins': [],
            'filters': '',
            'definitions': [],
        }
        
        # Load table metadata
        table_file = os.path.join(kb_dir, 'table_metadata.json')
        if os.path.exists(table_file):
            try:
                with open(table_file, 'r', encoding='utf-8') as f:
                    metadata['tables'] = json.load(f)
            except Exception as e:
                print(f"  ⚠️ Error loading table metadata: {e}")
        
        # Load column metadata
        column_file = os.path.join(kb_dir, 'column_metadata.json')
        if os.path.exists(column_file):
            try:
                with open(column_file, 'r', encoding='utf-8') as f:
                    metadata['columns'] = json.load(f)
            except Exception as e:
                print(f"  ⚠️ Error loading column metadata: {e}")
        
        # Load joining conditions
        join_file = os.path.join(kb_dir, 'joining_conditions.json')
        if os.path.exists(join_file):
            try:
                with open(join_file, 'r', encoding='utf-8') as f:
                    metadata['joins'] = json.load(f)
            except Exception as e:
                print(f"  ⚠️ Error loading joining conditions: {e}")
        
        # Load filter conditions
        filter_file = os.path.join(kb_dir, 'filter_conditions.txt')
        if os.path.exists(filter_file):
            try:
                with open(filter_file, 'r', encoding='utf-8') as f:
                    metadata['filters'] = f.read()
            except Exception as e:
                print(f"  ⚠️ Error loading filter conditions: {e}")
        
        # Load definitions
        definitions_file = os.path.join(kb_dir, 'definitions.json')
        if os.path.exists(definitions_file):
            try:
                with open(definitions_file, 'r', encoding='utf-8') as f:
                    metadata['definitions'] = json.load(f)
            except Exception as e:
                print(f"  ⚠️ Error loading definitions: {e}")
        
        return metadata
    
    def _extract_json_array(self, text: str) -> List[Dict]:
        """Try to extract JSON array from text response."""
        try:
            # Look for JSON array in the text
            start = text.find('[')
            end = text.rfind(']') + 1
            if start >= 0 and end > start:
                return json.loads(text[start:end])
        except:
            pass
        
        # Return empty array as fallback
        return []
    
    def _generate_fallback(
        self,
        vertical: Optional[str],
        sub_vertical: Optional[str],
        metadata: Dict[str, Any],
        error: str
    ) -> Dict[str, Any]:
        """Generate fallback instruction set when LLM fails."""
        vertical_info = VERTICAL_CONTEXT.get(vertical, {})
        
        # Build basic instructions from metadata
        tables_list = '\n'.join([
            f"- {t.get('table_name', 'unknown')}: {t.get('table_description', '')[:100]}"
            for t in metadata['tables'][:10]
        ])
        
        joins_list = '\n'.join([
            f"- {j.get('table_1', '')} <-> {j.get('table_2', '')}: {j.get('join_condition', '')}"
            for j in metadata['joins'][:10]
        ])
        
        return {
            'generated_at': datetime.now().isoformat(),
            'version': '2.0-fallback',
            'generation_method': 'Template (LLM unavailable)',
            'error': error,
            'purpose': 'SQL Query Generation Agent Instructions',
            'context': {
                'vertical': {
                    'id': vertical or 'general',
                    'name': vertical_info.get('name', 'General Analytics'),
                },
                'sub_vertical': sub_vertical,
            },
            'instructions': [
                {
                    'category': 'Available Tables',
                    'priority': 'HIGH',
                    'content': f"The following tables are available:\n\n{tables_list}"
                },
                {
                    'category': 'Join Patterns',
                    'priority': 'MEDIUM',
                    'content': f"Use these join patterns:\n\n{joins_list}"
                },
                {
                    'category': 'General Guidelines',
                    'priority': 'HIGH',
                    'content': """
1. Always use fully qualified table names (catalog.schema.table)
2. Include partition filters (dt or day_id) for performance
3. Use CTEs for complex queries
4. Round percentages to 2 decimal places
5. Order results by date then primary dimension
"""
                },
            ],
            'example_queries': [],
            'metadata_summary': {
                'tables_count': len(metadata['tables']),
                'columns_count': len(metadata['columns']),
                'joins_count': len(metadata['joins']),
                'definitions_count': len(metadata['definitions']),
            },
        }


def generate_instruction_set(
    vertical: Optional[str] = None,
    sub_vertical: Optional[str] = None,
    kb_dir: str = "extracted_meta/knowledge_base",
    api_key: str = None
) -> Dict[str, Any]:
    """
    Generate instruction set using LLM.
    
    Args:
        vertical: Business vertical ID
        sub_vertical: Sub-vertical name
        kb_dir: Knowledge base directory
        api_key: Optional API key override
        
    Returns:
        Complete instruction set dictionary
    """
    generator = InstructionSetGenerator(api_key=api_key)
    return generator.generate(vertical, sub_vertical, kb_dir)


def generate_instruction_set_file(
    vertical: Optional[str] = None,
    sub_vertical: Optional[str] = None,
    kb_dir: str = "extracted_meta/knowledge_base",
    output_format: str = "json",
    api_key: str = None
) -> str:
    """
    Generate instruction set and save to file.
    
    Args:
        vertical: Business vertical ID
        sub_vertical: Sub-vertical name
        kb_dir: Knowledge base directory
        output_format: Output format ('json' or 'txt')
        api_key: Optional API key override
        
    Returns:
        Path to generated file
    """
    instruction_set = generate_instruction_set(vertical, sub_vertical, kb_dir, api_key)
    
    # Create output directory if needed
    os.makedirs(kb_dir, exist_ok=True)
    
    if output_format == 'json':
        output_file = os.path.join(kb_dir, 'instruction_set.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(instruction_set, f, indent=2, ensure_ascii=False)
    else:
        output_file = os.path.join(kb_dir, 'instruction_set.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(_format_as_text(instruction_set))
    
    print(f"✅ Instruction set saved: {output_file}")
    return output_file


def _format_as_text(instruction_set: Dict[str, Any]) -> str:
    """Format instruction set as readable text."""
    lines = []
    
    # Header
    lines.append("=" * 80)
    lines.append("SQL QUERY GENERATION AGENT - INSTRUCTION SET")
    lines.append("=" * 80)
    lines.append(f"\nGenerated: {instruction_set.get('generated_at', 'N/A')}")
    lines.append(f"Version: {instruction_set.get('version', '2.0')}")
    lines.append(f"Generation Method: {instruction_set.get('generation_method', 'LLM')}")
    lines.append("")
    
    # Context
    context = instruction_set.get('context', {})
    if context.get('vertical'):
        v = context['vertical']
        lines.append("-" * 40)
        lines.append("BUSINESS CONTEXT")
        lines.append("-" * 40)
        lines.append(f"Vertical: {v.get('name', 'N/A')}")
        if v.get('description'):
            lines.append(f"Description: {v.get('description')}")
        if v.get('domain_context'):
            lines.append(f"Domain: {v.get('domain_context')}")
        if context.get('sub_vertical'):
            lines.append(f"Sub-Vertical: {context.get('sub_vertical')}")
        lines.append("")
    
    # Instructions
    lines.append("-" * 40)
    lines.append("INSTRUCTIONS")
    lines.append("-" * 40)
    
    for instr in instruction_set.get('instructions', []):
        lines.append(f"\n### {instr.get('category', 'General')} [{instr.get('priority', 'MEDIUM')}]")
        lines.append("")
        lines.append(instr.get('content', ''))
    
    # Example Queries
    examples = instruction_set.get('example_queries', [])
    if examples:
        lines.append("\n" + "-" * 40)
        lines.append("EXAMPLE QUERIES")
        lines.append("-" * 40)
        
        for i, ex in enumerate(examples, 1):
            lines.append(f"\n### Example {i}: {ex.get('description', '')}")
            if ex.get('explanation'):
                lines.append(f"Purpose: {ex.get('explanation')}")
            lines.append("\n```sql")
            lines.append(ex.get('query', ''))
            lines.append("```")
    
    # Metadata Summary
    summary = instruction_set.get('metadata_summary', {})
    if summary:
        lines.append("\n" + "-" * 40)
        lines.append("METADATA SUMMARY")
        lines.append("-" * 40)
        lines.append(f"Tables: {summary.get('tables_count', 0)}")
        lines.append(f"Columns: {summary.get('columns_count', 0)}")
        lines.append(f"Joins: {summary.get('joins_count', 0)}")
        lines.append(f"Definitions: {summary.get('definitions_count', 0)}")
    
    lines.append("\n" + "=" * 80)
    lines.append("END OF INSTRUCTION SET")
    lines.append("=" * 80)
    
    return '\n'.join(lines)


def get_available_verticals() -> List[Dict[str, Any]]:
    """Get list of available verticals."""
    return [
        {
            'id': v_id,
            'name': v_info['name'],
            'description': v_info['description'],
        }
        for v_id, v_info in VERTICAL_CONTEXT.items()
    ]


# CLI interface
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate SQL Agent Instruction Set (LLM-Powered)')
    parser.add_argument('--vertical', '-v', type=str, help='Business vertical ID')
    parser.add_argument('--sub-vertical', '-s', type=str, help='Sub-vertical name')
    parser.add_argument('--kb-dir', type=str, default='extracted_meta/knowledge_base',
                        help='Knowledge base directory')
    parser.add_argument('--format', '-f', type=str, choices=['json', 'txt'], default='json',
                        help='Output format')
    parser.add_argument('--list-verticals', action='store_true', help='List available verticals')
    
    args = parser.parse_args()
    
    if args.list_verticals:
        print("\nAvailable Verticals:")
        print("-" * 40)
        for v in get_available_verticals():
            print(f"\n{v['id']}: {v['name']}")
            print(f"  {v['description']}")
    else:
        output_file = generate_instruction_set_file(
            vertical=args.vertical,
            sub_vertical=args.sub_vertical,
            kb_dir=args.kb_dir,
            output_format=args.format
        )
        print(f"\nInstruction set saved to: {output_file}")
