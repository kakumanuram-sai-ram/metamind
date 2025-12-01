"""
Test script to validate tables from dashboard 476 using SHOW TABLES

Uses existing 476_json.json file to demonstrate:
1. Tables extracted from JSON
2. Actual validation using SHOW TABLES for each database
3. Tables that exist vs don't exist
"""
import json
import sys
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from table_validator import validate_tables
from sql_parser import normalize_table_name


def extract_tables_from_json(json_file: str):
    """Extract unique tables from dashboard JSON file"""
    print(f"\n📂 Reading: {json_file}")
    
    with open(json_file, 'r', encoding='utf-8') as f:
        dashboard_data = json.load(f)
    
    dashboard_title = dashboard_data.get('dashboard_title', 'Unknown')
    charts = dashboard_data.get('charts', [])
    
    print(f"📊 Dashboard: {dashboard_title}")
    print(f"📈 Total charts: {len(charts)}")
    
    # Extract tables from SQL queries
    tables = set()
    
    for chart in charts:
        sql_query = chart.get('sql_query', '')
        if not sql_query:
            continue
        
        # Simple extraction: look for FROM and JOIN clauses
        import re
        
        # Find FROM table_name
        from_matches = re.findall(r'FROM\s+([^\s,\(\)]+)', sql_query, re.IGNORECASE)
        for match in from_matches:
            cleaned = match.strip().strip('"').strip("'").strip('`')
            if cleaned and not cleaned.upper() in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'LIMIT']:
                # Normalize the table name
                normalized = normalize_table_name(cleaned)
                if normalized:
                    tables.add(normalized)
        
        # Find JOIN table_name
        join_matches = re.findall(r'JOIN\s+([^\s,\(\)]+)', sql_query, re.IGNORECASE)
        for match in join_matches:
            cleaned = match.strip().strip('"').strip("'").strip('`')
            if cleaned and not cleaned.upper() in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'LIMIT', 'ON']:
                normalized = normalize_table_name(cleaned)
                if normalized:
                    tables.add(normalized)
    
    return sorted(list(tables))


def main():
    """Main test function"""
    print("="*80)
    print("🧪 TABLE EXTRACTION & VALIDATION TEST - Dashboard 476")
    print("="*80)
    
    # Path to dashboard 476 JSON
    json_file = "extracted_meta/476/476_json.json"
    
    try:
        # Step 1: Extract tables from JSON
        print("\n" + "─"*80)
        print("STEP 1: Extract Tables from JSON")
        print("─"*80)
        
        tables_before = extract_tables_from_json(json_file)
        
        print(f"\n✅ Extracted {len(tables_before)} unique tables:")
        print()
        for i, table in enumerate(tables_before, 1):
            print(f"  {i:2}. {table}")
        
        if not tables_before:
            print("  ⚠️  No tables found!")
            return 1
        
        # Step 2: Validate tables using SHOW TABLES
        print("\n" + "─"*80)
        print("STEP 2: Validate Tables Using SHOW TABLES")
        print("─"*80)
        
        print(f"\n📋 Validation Strategy:")
        print(f"   For each unique schema (e.g., user_paytm_payments, cdo, tpap_pms):")
        print(f"   1. Run: SHOW TABLES FROM \"hive\".\"<schema>\"")
        print(f"   2. Collect all tables from that schema")
        print(f"   3. Check if our extracted tables exist in the results")
        print()
        
        # Run actual validation
        valid_tables = validate_tables(tables_before)
        invalid_tables = set(tables_before) - set(valid_tables)
        
        # Step 3: Show results
        print("\n" + "─"*80)
        print("STEP 3: Validation Results")
        print("─"*80)
        
        print(f"\n📊 Summary:")
        print(f"   Total tables before validation: {len(tables_before)}")
        print(f"   ✅ Valid tables (exist in schemas): {len(valid_tables)}")
        print(f"   ❌ Invalid tables (don't exist): {len(invalid_tables)}")
        
        if valid_tables:
            print(f"\n✅ VALID Tables ({len(valid_tables)}):")
            print("   These tables EXIST (confirmed via SHOW TABLES):")
            for i, table in enumerate(sorted(valid_tables), 1):
                print(f"   {i:2}. ✓ {table}")
        
        if invalid_tables:
            print(f"\n❌ INVALID Tables ({len(invalid_tables)}):")
            print("   These tables do NOT exist (CTE aliases/temp tables):")
            for i, table in enumerate(sorted(invalid_tables), 1):
                print(f"   {i:2}. ✗ {table}")
        
        # Step 4: Cost impact
        print("\n" + "─"*80)
        print("STEP 4: Cost Impact Analysis")
        print("─"*80)
        
        print(f"\n💰 LLM Metadata Generation Cost:")
        print(f"   Without validation: {len(tables_before)} tables × $0.03 = ${len(tables_before) * 0.03:.2f}")
        print(f"   With validation:    {len(valid_tables)} tables × $0.03 = ${len(valid_tables) * 0.03:.2f}")
        
        if invalid_tables:
            savings = len(invalid_tables) * 0.03
            percentage = (len(invalid_tables) / len(tables_before)) * 100
            print(f"   💵 SAVINGS:         ${savings:.2f} ({percentage:.1f}% reduction)")
            print(f"\n   🎯 By validating first, we AVOID making {len(invalid_tables)} unnecessary LLM calls!")
        else:
            print(f"   ℹ️  No savings (all tables are valid)")
        
        print("\n" + "="*80)
        print("✅ VALIDATION TEST COMPLETED SUCCESSFULLY!")
        print("="*80)
        
        print(f"\n📊 Dashboard 476 Final Summary:")
        print(f"   - Dashboard: UPI Profile wise MAU Distribution")
        print(f"   - Total tables extracted: {len(tables_before)}")
        print(f"   - Valid tables (real tables): {len(valid_tables)}")
        print(f"   - Invalid tables (CTE aliases): {len(invalid_tables)}")
        print(f"   - LLM cost savings: ${len(invalid_tables) * 0.03:.2f} ({(len(invalid_tables) / len(tables_before)) * 100:.1f}%)")
        
        return 0
        
    except FileNotFoundError:
        print(f"\n❌ Error: File not found: {json_file}")
        print(f"   Please ensure dashboard 476 has been extracted.")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
