"""
Knowledge Base Builder

This module converts merged metadata into a knowledge base format suitable for
LLM context injection, documentation, and business user reference.
"""
import os
import json
import zipfile
import pandas as pd
from typing import Dict, List, Optional
from progress_tracker import get_progress_tracker


class KnowledgeBaseBuilder:
    """
    Builds a knowledge base from merged metadata.
    """
    
    def __init__(self, merged_metadata_dir: str = "extracted_meta/merged_metadata"):
        """
        Initialize the knowledge base builder.
        
        Args:
            merged_metadata_dir: Directory containing merged metadata files
        """
        self.merged_dir = merged_metadata_dir
        self.kb_dir = "extracted_meta/knowledge_base"
        os.makedirs(self.kb_dir, exist_ok=True)
        self.progress_tracker = get_progress_tracker()
    
    def build_from_merged_metadata(self):
        """
        Build knowledge base from merged metadata files.
        Creates specific JSON files and a compressed zip archive.
        """
        # Initialize KB build progress
        self.progress_tracker.start_kb_build()
        
        print("\n" + "="*80)
        print("KNOWLEDGE BASE BUILDER")
        print("="*80)
        
        # Load merged metadata files
        table_metadata_file = f"{self.merged_dir}/consolidated_table_metadata.csv"
        columns_metadata_file = f"{self.merged_dir}/consolidated_columns_metadata.csv"
        joining_conditions_file = f"{self.merged_dir}/consolidated_joining_conditions.csv"
        definitions_file = f"{self.merged_dir}/consolidated_definitions.csv"
        filter_conditions_file = f"{self.merged_dir}/consolidated_filter_conditions.txt"
        
        # Convert merged metadata to knowledge base format
        print("\n[1/5] Converting table metadata...")
        self.progress_tracker.update_kb_build_status('tables')
        if os.path.exists(table_metadata_file):
            self._convert_table_metadata_to_json(table_metadata_file)
        else:
            print("  ⚠️  Table metadata file not found, creating empty file")
            self._create_empty_table_metadata_json()
        
        print("\n[2/5] Converting column metadata...")
        self.progress_tracker.update_kb_build_status('columns')
        if os.path.exists(columns_metadata_file):
            self._convert_column_metadata_to_json(columns_metadata_file)
        else:
            print("  ⚠️  Column metadata file not found, creating empty file")
            self._create_empty_column_metadata_json()
        
        print("\n[3/5] Converting joining conditions...")
        self.progress_tracker.update_kb_build_status('joins')
        if os.path.exists(joining_conditions_file):
            self._convert_joining_conditions_to_json(joining_conditions_file)
        else:
            print("  ⚠️  Joining conditions file not found, creating empty file")
            self._create_empty_joining_conditions_json()
        
        print("\n[4/5] Converting definitions...")
        self.progress_tracker.update_kb_build_status('definitions')
        if os.path.exists(definitions_file):
            self._convert_definitions_to_json(definitions_file)
        else:
            print("  ⚠️  Definitions file not found, creating empty file")
            self._create_empty_definitions_json()
        
        print("\n[5/5] Converting filter conditions...")
        self.progress_tracker.update_kb_build_status('filter_conditions')
        if os.path.exists(filter_conditions_file):
            self._copy_filter_conditions(filter_conditions_file)
        else:
            print("  ⚠️  Filter conditions file not found, creating empty file")
            self._create_empty_filter_conditions_txt()
        
        # Create empty business_context.json
        print("\n[6/6] Creating business_context.json...")
        self._create_empty_business_context_json()
        
        # Create empty validations.json
        print("\n[7/7] Creating validations.json...")
        self._create_empty_validations_json()
        
        # Create compressed zip file
        print("\n[8/8] Creating compressed zip archive...")
        zip_file = self._create_zip_archive()
        
        # Mark KB build as completed
        self.progress_tracker.complete_kb_build()
        
        print("\n" + "="*80)
        print("KNOWLEDGE BASE BUILD COMPLETE")
        print("="*80)
        print(f"✅ All files saved to: {self.kb_dir}/")
        print(f"✅ Compressed archive: {zip_file}")
        
        return {
            'kb_dir': self.kb_dir,
            'zip_file': zip_file
        }
    
    def _convert_table_metadata_to_json(self, table_metadata_file: str):
        """Convert table metadata CSV to JSON format."""
        df = pd.read_csv(table_metadata_file)
        
        # Convert DataFrame to list of dicts
        tables_list = df.to_dict('records')
        
        # Save as JSON
        output_file = f"{self.kb_dir}/table_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tables_list, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Converted {len(tables_list)} tables to table_metadata.json")
    
    def _create_empty_table_metadata_json(self):
        """Create empty table_metadata.json file."""
        output_file = f"{self.kb_dir}/table_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created empty table_metadata.json")
    
    def _convert_column_metadata_to_json(self, columns_metadata_file: str):
        """Convert column metadata CSV to JSON format."""
        try:
            df = pd.read_csv(columns_metadata_file)
            if len(df) == 0:
                columns_list = []
            else:
                # Convert DataFrame to list of dicts
                columns_list = df.to_dict('records')
        except (pd.errors.EmptyDataError, ValueError):
            columns_list = []
        
        # Save as JSON
        output_file = f"{self.kb_dir}/column_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(columns_list, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Converted {len(columns_list)} columns to column_metadata.json")
    
    def _create_empty_column_metadata_json(self):
        """Create empty column_metadata.json file."""
        output_file = f"{self.kb_dir}/column_metadata.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created empty column_metadata.json")
    
    def _convert_joining_conditions_to_json(self, joining_conditions_file: str):
        """Convert joining conditions CSV to JSON format."""
        try:
            df = pd.read_csv(joining_conditions_file)
            if len(df) == 0:
                joins_list = []
            else:
                # Convert DataFrame to list of dicts
                joins_list = df.to_dict('records')
        except (pd.errors.EmptyDataError, ValueError, FileNotFoundError):
            joins_list = []
        
        # Save as JSON
        output_file = f"{self.kb_dir}/joining_conditions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(joins_list, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Converted {len(joins_list)} joining conditions to joining_conditions.json")
    
    def _create_empty_joining_conditions_json(self):
        """Create empty joining_conditions.json file."""
        output_file = f"{self.kb_dir}/joining_conditions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created empty joining_conditions.json")
    
    def _convert_definitions_to_json(self, definitions_file: str):
        """Convert definitions CSV to JSON format."""
        try:
            df = pd.read_csv(definitions_file)
            if len(df) == 0:
                definitions_list = []
            else:
                # Convert DataFrame to list of dicts
                definitions_list = df.to_dict('records')
        except (pd.errors.EmptyDataError, ValueError):
            definitions_list = []
        
        # Save as JSON
        output_file = f"{self.kb_dir}/definitions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(definitions_list, f, indent=2, ensure_ascii=False)
        
        print(f"   ✅ Converted {len(definitions_list)} definitions to definitions.json")
    
    def _create_empty_definitions_json(self):
        """Create empty definitions.json file."""
        output_file = f"{self.kb_dir}/definitions.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created empty definitions.json")
    
    def _copy_filter_conditions(self, filter_conditions_file: str):
        """Copy filter conditions text file."""
        with open(filter_conditions_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Save filter conditions
        output_file = f"{self.kb_dir}/filter_conditions.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   ✅ Copied filter conditions to filter_conditions.txt")
    
    def _create_empty_filter_conditions_txt(self):
        """Create empty filter_conditions.txt file."""
        output_file = f"{self.kb_dir}/filter_conditions.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("")
        print(f"   ✅ Created empty filter_conditions.txt")
    
    def _create_empty_business_context_json(self):
        """Create empty business_context.json file."""
        output_file = f"{self.kb_dir}/business_context.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created empty business_context.json")
    
    def _create_empty_validations_json(self):
        """Create empty validations.json file."""
        output_file = f"{self.kb_dir}/validations.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({}, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created empty validations.json")
    
    def _create_zip_archive(self) -> str:
        """Create compressed zip archive with all knowledge base files."""
        zip_file = f"{self.kb_dir}/knowledge_base.zip"
        
        files_to_zip = [
            'table_metadata.json',
            'column_metadata.json',
            'joining_conditions.json',
            'definitions.json',
            'filter_conditions.txt',
            'business_context.json',
            'validations.json'
        ]
        
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename in files_to_zip:
                file_path = f"{self.kb_dir}/{filename}"
                if os.path.exists(file_path):
                    zipf.write(file_path, filename)
                    print(f"   ✅ Added {filename} to zip")
                else:
                    print(f"   ⚠️  {filename} not found, skipping")
        
        zip_size = os.path.getsize(zip_file)
        print(f"   ✅ Created zip archive: {zip_file} ({zip_size:,} bytes)")
        
        return zip_file

