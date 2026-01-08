#!/usr/bin/env python3
"""
GraphRAG Metadata Validator
============================
Purpose: Validate document metadata BEFORE importing to database
Author: FR03.3 Team
Date: 2025-12-26

Validates metadata structure from FR03.1 export format:
- Checks required fields for GraphRAG
- Validates hierarchy levels
- Checks relationships structure
- Reports missing/invalid data

Usage:
    # Single file
    python validate_metadata_local.py path/to/document.json
    
    # Directory scan
    python validate_metadata_local.py path/to/exports/
    
    # With export report
    python validate_metadata_local.py path/to/exports/ --export report.csv
"""

import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
import argparse

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

    @staticmethod
    def success(text):
        return f"{Colors.GREEN}{text}{Colors.END}"
    
    @staticmethod
    def error(text):
        return f"{Colors.RED}{text}{Colors.END}"
    
    @staticmethod
    def warning(text):
        return f"{Colors.YELLOW}{text}{Colors.END}"
    
    @staticmethod
    def info(text):
        return f"{Colors.BLUE}{text}{Colors.END}"


@dataclass
class ValidationRule:
    """Single validation rule"""
    name: str
    severity: str  # 'critical', 'error', 'warning', 'info'
    description: str
    passed: bool = False
    message: str = ""
    field_path: str = ""


@dataclass
class ValidationResult:
    """Validation result for a single document"""
    file_path: str
    document_id: str = ""
    title: str = ""
    status: str = "FAIL"  # 'PASS', 'FAIL', 'WARNING'
    
    critical_issues: List[ValidationRule] = field(default_factory=list)
    errors: List[ValidationRule] = field(default_factory=list)
    warnings: List[ValidationRule] = field(default_factory=list)
    info: List[ValidationRule] = field(default_factory=list)
    
    graph_ready_score: float = 0.0  # 0-100%
    
    def add_rule(self, rule: ValidationRule):
        """Add validation rule result"""
        if rule.severity == 'critical':
            self.critical_issues.append(rule)
        elif rule.severity == 'error':
            self.errors.append(rule)
        elif rule.severity == 'warning':
            self.warnings.append(rule)
        else:
            self.info.append(rule)
    
    def calculate_score(self):
        """Calculate GraphRAG readiness score"""
        total_checks = len(self.critical_issues) + len(self.errors) + len(self.warnings)
        if total_checks == 0:
            self.graph_ready_score = 100.0
            return
        
        passed_critical = sum(1 for r in self.critical_issues if r.passed)
        passed_errors = sum(1 for r in self.errors if r.passed)
        passed_warnings = sum(1 for r in self.warnings if r.passed)
        
        # Weight: Critical=50%, Error=30%, Warning=20%
        critical_score = (passed_critical / len(self.critical_issues) * 50) if self.critical_issues else 50
        error_score = (passed_errors / len(self.errors) * 30) if self.errors else 30
        warning_score = (passed_warnings / len(self.warnings) * 20) if self.warnings else 20
        
        self.graph_ready_score = critical_score + error_score + warning_score
        
        # Determine status
        if len(self.critical_issues) > 0 and not all(r.passed for r in self.critical_issues):
            self.status = "FAIL"
        elif len(self.errors) > 0 and not all(r.passed for r in self.errors):
            self.status = "FAIL"
        elif len(self.warnings) > 0 and not all(r.passed for r in self.warnings):
            self.status = "WARNING"
        else:
            self.status = "PASS"


class MetadataValidator:
    """Validate metadata for GraphRAG readiness"""
    
    def __init__(self):
        self.results: List[ValidationResult] = []
    
    def validate_file(self, file_path: str) -> ValidationResult:
        """Validate single JSON file"""
        result = ValidationResult(file_path=file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Extract basic info
            result.document_id = metadata.get('document_id', 'N/A')
            result.title = metadata.get('title', 'N/A')
            
            # Run validation rules
            self._validate_structure(metadata, result)
            self._validate_identification(metadata, result)
            self._validate_hierarchy(metadata, result)
            self._validate_relationships(metadata, result)
            self._validate_graph_context(metadata, result)
            self._validate_governance(metadata, result)
            
            # Calculate score
            result.calculate_score()
            
        except json.JSONDecodeError as e:
            rule = ValidationRule(
                name="JSON Parse",
                severity="critical",
                description="File must be valid JSON",
                passed=False,
                message=f"JSON parse error: {str(e)}",
                field_path="N/A"
            )
            result.add_rule(rule)
            result.status = "FAIL"
            result.graph_ready_score = 0.0
        
        except Exception as e:
            rule = ValidationRule(
                name="File Read",
                severity="critical",
                description="File must be readable",
                passed=False,
                message=f"Error reading file: {str(e)}",
                field_path="N/A"
            )
            result.add_rule(rule)
            result.status = "FAIL"
            result.graph_ready_score = 0.0
        
        self.results.append(result)
        return result
    
    def _validate_structure(self, metadata: Dict, result: ValidationResult):
        """Validate basic metadata structure"""
        
        # Critical: document_id exists
        rule = ValidationRule(
            name="Document ID",
            severity="critical",
            description="Must have unique document_id",
            field_path="document_id"
        )
        rule.passed = 'document_id' in metadata and metadata['document_id']
        rule.message = "Found" if rule.passed else "Missing document_id"
        result.add_rule(rule)
        
        # Critical: title exists
        rule = ValidationRule(
            name="Title",
            severity="critical",
            description="Must have document title",
            field_path="title"
        )
        rule.passed = 'title' in metadata and metadata['title']
        rule.message = "Found" if rule.passed else "Missing title"
        result.add_rule(rule)
    
    def _validate_identification(self, metadata: Dict, result: ValidationResult):
        """Validate identification section"""
        
        identification = metadata.get('identification', {})
        
        # Error: document_type
        rule = ValidationRule(
            name="Document Type",
            severity="error",
            description="Must specify document type",
            field_path="identification.document_type"
        )
        rule.passed = 'document_type' in identification and identification['document_type']
        rule.message = f"Found: {identification.get('document_type', 'N/A')}" if rule.passed else "Missing document_type"
        result.add_rule(rule)
        
        # Warning: task_code (important for project relationships)
        rule = ValidationRule(
            name="Task Code",
            severity="warning",
            description="Task code helps link project documents",
            field_path="identification.task_code"
        )
        rule.passed = 'task_code' in identification and identification['task_code']
        rule.message = f"Found: {identification.get('task_code', 'N/A')}" if rule.passed else "Missing task_code - harder to link project docs"
        result.add_rule(rule)
        
        # Warning: issue_date
        rule = ValidationRule(
            name="Issue Date",
            severity="warning",
            description="Issue date helps chronological relationships",
            field_path="identification.issue_date"
        )
        rule.passed = 'issue_date' in identification and identification['issue_date']
        rule.message = f"Found: {identification.get('issue_date', 'N/A')}" if rule.passed else "Missing issue_date"
        result.add_rule(rule)
    
    def _validate_hierarchy(self, metadata: Dict, result: ValidationResult):
        """Validate hierarchy section - CRITICAL for GraphRAG"""
        
        hierarchy = metadata.get('hierarchy', {})
        
        # Critical: rank_level
        rule = ValidationRule(
            name="Hierarchy Level",
            severity="critical",
            description="Must have hierarchy rank_level (0-10) for graph structure",
            field_path="hierarchy.rank_level"
        )
        rank_level = hierarchy.get('rank_level')
        rule.passed = rank_level is not None and isinstance(rank_level, int) and 0 <= rank_level <= 10
        if rule.passed:
            rule.message = f"Found level {rank_level} - {self._get_level_name(rank_level)}"
        else:
            rule.message = "Missing or invalid rank_level - CANNOT build graph hierarchy"
        result.add_rule(rule)
        
        # Warning: parent_id
        rule = ValidationRule(
            name="Parent ID",
            severity="warning",
            description="Parent ID creates direct hierarchy links",
            field_path="hierarchy.parent_id"
        )
        parent_id = hierarchy.get('parent_id')
        rule.passed = parent_id is not None
        rule.message = f"Found: {parent_id}" if rule.passed else "No parent_id - will rely on other linking methods"
        result.add_rule(rule)
    
    def _validate_relationships(self, metadata: Dict, result: ValidationResult):
        """Validate relationships section - KEY for GraphRAG"""
        
        relationships = metadata.get('relationships', {})
        
        # Error: relates_to array
        rule = ValidationRule(
            name="Relationships",
            severity="error",
            description="relates_to array links documents",
            field_path="relationships.relates_to"
        )
        relates_to = relationships.get('relates_to', [])
        rule.passed = isinstance(relates_to, list) and len(relates_to) > 0
        if rule.passed:
            rule.message = f"Found {len(relates_to)} relationship(s): {', '.join(relates_to[:3])}"
        else:
            rule.message = "No relates_to - document will be isolated in graph"
        result.add_rule(rule)
    
    def _validate_graph_context(self, metadata: Dict, result: ValidationResult):
        """Validate graph_context section - IMPORTANT for GraphRAG"""
        
        graph_context = metadata.get('graph_context', {})
        
        # Error: related_projects
        rule = ValidationRule(
            name="Related Projects",
            severity="error",
            description="related_projects links documents in same project",
            field_path="graph_context.related_projects"
        )
        related_projects = graph_context.get('related_projects', [])
        rule.passed = isinstance(related_projects, list) and len(related_projects) > 0
        if rule.passed:
            rule.message = f"Found {len(related_projects)} project(s): {', '.join(related_projects[:3])}"
        else:
            rule.message = "No related_projects - harder to group project documents"
        result.add_rule(rule)
        
        # Warning: implements
        rule = ValidationRule(
            name="Implements",
            severity="warning",
            description="implements field shows execution relationship",
            field_path="graph_context.implements"
        )
        implements = graph_context.get('implements')
        rule.passed = implements is not None
        rule.message = f"Implements: {implements}" if rule.passed else "No implements field"
        result.add_rule(rule)
        
        # Warning: referenced_by
        rule = ValidationRule(
            name="Referenced By",
            severity="warning",
            description="referenced_by shows incoming citations",
            field_path="graph_context.referenced_by"
        )
        referenced_by = graph_context.get('referenced_by', [])
        rule.passed = isinstance(referenced_by, list) and len(referenced_by) > 0
        rule.message = f"Referenced by {len(referenced_by)} document(s)" if rule.passed else "No incoming references"
        result.add_rule(rule)
    
    def _validate_governance(self, metadata: Dict, result: ValidationResult):
        """Validate governance section"""
        
        governance = metadata.get('governance', {})
        
        # Warning: governing_laws
        rule = ValidationRule(
            name="Governing Laws",
            severity="warning",
            description="governing_laws creates legal hierarchy",
            field_path="governance.governing_laws"
        )
        governing_laws = governance.get('governing_laws', [])
        rule.passed = isinstance(governing_laws, list) and len(governing_laws) > 0
        if rule.passed:
            rule.message = f"Governed by {len(governing_laws)} law(s): {', '.join(governing_laws[:3])}"
        else:
            rule.message = "No governing_laws - missing legal hierarchy"
        result.add_rule(rule)
        
        # Info: superseded_by
        rule = ValidationRule(
            name="Superseded By",
            severity="info",
            description="superseded_by shows replacement relationship",
            field_path="governance.superseded_by"
        )
        superseded_by = governance.get('superseded_by')
        rule.passed = superseded_by is not None
        rule.message = f"Superseded by: {superseded_by}" if rule.passed else "Document is current (not superseded)"
        result.add_rule(rule)
    
    def _get_level_name(self, level: int) -> str:
        """Get hierarchy level name"""
        names = {
            0: "Constitutional",
            1: "Framework",
            2: "Regulation",
            3: "Planning",
            4: "Project Approval",
            5: "Project Execution",
        }
        return names.get(level, f"Level {level}")
    
    def scan_directory(self, directory: str, pattern: str = "*_document.json") -> List[ValidationResult]:
        """Scan directory for document JSON files"""
        path = Path(directory)
        
        if not path.exists():
            print(Colors.error(f"Directory not found: {directory}"))
            return []
        
        json_files = list(path.glob(pattern))
        
        if not json_files:
            print(Colors.warning(f"No files matching '{pattern}' found in {directory}"))
            return []
        
        print(Colors.info(f"Found {len(json_files)} files to validate\n"))
        
        results = []
        for i, file_path in enumerate(json_files, 1):
            print(f"[{i}/{len(json_files)}] Validating: {file_path.name}...", end=' ')
            result = self.validate_file(str(file_path))
            
            # Status indicator
            if result.status == "PASS":
                print(Colors.success("✓ PASS"))
            elif result.status == "WARNING":
                print(Colors.warning("⚠ WARNING"))
            else:
                print(Colors.error("✗ FAIL"))
            
            results.append(result)
        
        return results
    
    def print_summary(self):
        """Print validation summary"""
        if not self.results:
            print(Colors.warning("No validation results to display"))
            return
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "PASS")
        warnings = sum(1 for r in self.results if r.status == "WARNING")
        failed = sum(1 for r in self.results if r.status == "FAIL")
        
        avg_score = sum(r.graph_ready_score for r in self.results) / total
        
        print("\n" + "="*70)
        print(Colors.BOLD + "VALIDATION SUMMARY" + Colors.END)
        print("="*70)
        print(f"Total files: {total}")
        print(f"  {Colors.success('✓ PASS')}: {passed} ({passed/total*100:.1f}%)")
        print(f"  {Colors.warning('⚠ WARNING')}: {warnings} ({warnings/total*100:.1f}%)")
        print(f"  {Colors.error('✗ FAIL')}: {failed} ({failed/total*100:.1f}%)")
        print(f"\nAverage GraphRAG Readiness: {avg_score:.1f}%")
        
        # Top issues
        all_issues = []
        for result in self.results:
            all_issues.extend(result.critical_issues)
            all_issues.extend(result.errors)
            all_issues.extend(result.warnings)
        
        failed_rules = [r for r in all_issues if not r.passed]
        
        if failed_rules:
            # Count by rule name
            issue_counts = {}
            for rule in failed_rules:
                key = f"{rule.name} ({rule.severity})"
                issue_counts[key] = issue_counts.get(key, 0) + 1
            
            print(f"\nTop Issues:")
            sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
            for issue, count in sorted_issues[:5]:
                print(f"  • {issue}: {count} file(s)")
        
        print("="*70 + "\n")
    
    def print_detailed_report(self, result: ValidationResult):
        """Print detailed validation report for single file"""
        print("\n" + "="*70)
        print(Colors.BOLD + f"DETAILED REPORT: {Path(result.file_path).name}" + Colors.END)
        print("="*70)
        print(f"Document ID: {result.document_id}")
        print(f"Title: {result.title}")
        print(f"Status: ", end='')
        
        if result.status == "PASS":
            print(Colors.success(result.status))
        elif result.status == "WARNING":
            print(Colors.warning(result.status))
        else:
            print(Colors.error(result.status))
        
        print(f"GraphRAG Readiness: {result.graph_ready_score:.1f}%")
        print()
        
        # Print issues by severity
        if result.critical_issues:
            print(Colors.error("CRITICAL ISSUES:"))
            for rule in result.critical_issues:
                self._print_rule(rule)
        
        if result.errors:
            print(Colors.error("ERRORS:"))
            for rule in result.errors:
                self._print_rule(rule)
        
        if result.warnings:
            print(Colors.warning("WARNINGS:"))
            for rule in result.warnings:
                self._print_rule(rule)
        
        if result.info:
            print(Colors.info("INFO:"))
            for rule in result.info:
                self._print_rule(rule)
        
        print("="*70 + "\n")
    
    def _print_rule(self, rule: ValidationRule):
        """Print single validation rule"""
        status = Colors.success("✓") if rule.passed else Colors.error("✗")
        print(f"  {status} {rule.name} ({rule.field_path})")
        print(f"    {rule.message}")
    
    def export_report(self, output_file: str):
        """Export validation report to CSV"""
        import csv
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                'File', 'Document ID', 'Title', 'Status', 'Score',
                'Critical Issues', 'Errors', 'Warnings', 'Details'
            ])
            
            # Data
            for result in self.results:
                critical_count = sum(1 for r in result.critical_issues if not r.passed)
                error_count = sum(1 for r in result.errors if not r.passed)
                warning_count = sum(1 for r in result.warnings if not r.passed)
                
                details = []
                for rule in result.critical_issues + result.errors + result.warnings:
                    if not rule.passed:
                        details.append(f"{rule.name}: {rule.message}")
                
                writer.writerow([
                    Path(result.file_path).name,
                    result.document_id,
                    result.title,
                    result.status,
                    f"{result.graph_ready_score:.1f}%",
                    critical_count,
                    error_count,
                    warning_count,
                    "; ".join(details)
                ])
        
        print(Colors.success(f"Report exported to: {output_file}"))


def main():
    parser = argparse.ArgumentParser(
        description="Validate document metadata for GraphRAG readiness"
    )
    parser.add_argument(
        'path',
        help="Path to JSON file or directory"
    )
    parser.add_argument(
        '--pattern',
        default='*_document.json',
        help="File pattern for directory scan (default: *_document.json)"
    )
    parser.add_argument(
        '--export',
        help="Export report to CSV file"
    )
    parser.add_argument(
        '--detailed',
        action='store_true',
        help="Show detailed report for each file"
    )
    
    args = parser.parse_args()
    
    validator = MetadataValidator()
    
    # Check if path is file or directory
    path = Path(args.path)
    
    if path.is_file():
        # Single file validation
        result = validator.validate_file(str(path))
        validator.print_detailed_report(result)
    
    elif path.is_dir():
        # Directory scan
        validator.scan_directory(str(path), args.pattern)
        
        # Print detailed reports if requested
        if args.detailed:
            for result in validator.results:
                validator.print_detailed_report(result)
        
        # Print summary
        validator.print_summary()
        
        # Export if requested
        if args.export:
            validator.export_report(args.export)
    
    else:
        print(Colors.error(f"Path not found: {args.path}"))
        sys.exit(1)
    
    # Exit with appropriate code
    if validator.results:
        failed_count = sum(1 for r in validator.results if r.status == "FAIL")
        sys.exit(1 if failed_count > 0 else 0)


if __name__ == '__main__':
    main()
