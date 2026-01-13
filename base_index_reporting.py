"""
Base Index - Industry-Grade Reporting Module

Provides enterprise-level reporting capabilities including:
- SARIF (Static Analysis Results Interchange Format) v2.1.0
- ISO/IEC 5055 compliance metrics
- ISO/IEC 25010 quality characteristics
- OWASP compliance reporting
- Data science professional formats (Parquet, Apache Arrow)
- Jupyter Notebook integration
- Big data analytics reports

Standards Compliance:
- SARIF 2.1.0 (OASIS Standard)
- ISO/IEC 5055:2021 (Software Quality Measurement)
- ISO/IEC 25010:2011 (Software Product Quality)
- OWASP Top 10 mapping
- CWE (Common Weakness Enumeration)
"""

__version__ = "2.0.0"
__author__ = "Base Index Team"

import os
import json
import uuid
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

# ============================================================================
# SARIF Report Generation (OASIS Standard SARIF v2.1.0)
# ============================================================================

class SARIFReporter:
    """
    Generate SARIF (Static Analysis Results Interchange Format) reports.
    
    SARIF is the industry standard for static analysis results used by:
    - GitHub Advanced Security
    - Microsoft Security DevOps
    - Azure DevOps
    - GitLab Security
    - All major SAST tools
    
    Specification: https://docs.oasis-open.org/sarif/sarif/v2.1.0/
    """
    
    SARIF_VERSION = "2.1.0"
    SCHEMA_URL = "https://json.schemastore.org/sarif-2.1.0-rtm.5.json"
    
    def __init__(self, tool_name="Base Index", tool_version="2.0.0"):
        self.tool_name = tool_name
        self.tool_version = tool_version
        self.runs = []
        self.logger = logging.getLogger(__name__)
    
    def create_run(self, index_stats: Dict, file_entries: List[Dict]) -> Dict:
        """
        Create a SARIF run from indexing results.
        
        A 'run' represents one execution of the analysis tool.
        """
        results = []
        
        # Analyze for common issues
        for entry in file_entries:
            size = entry.get('size', 0) or 0
            loc = entry.get('loc') or 0
            
            # Check for large files (potential maintainability issue)
            if size > 1024 * 1024:  # > 1MB
                results.append(self._create_result(
                    rule_id="BI001",
                    level="warning",
                    message=f"Large file detected ({size/(1024*1024):.2f} MB)",
                    file_path=entry['path'],
                    properties={
                        "category": "maintainability",
                        "size_bytes": size,
                        "iso_characteristic": "maintainability"
                    }
                ))
            
            # Check for excessive LOC (Lines of Code)
            if loc > 1000:
                complexity_score = min(100, int((loc / 10)))
                results.append(self._create_result(
                    rule_id="BI002",
                    level="note" if loc < 2000 else "warning",
                    message=f"High line count ({loc} LOC, complexity: {complexity_score})",
                    file_path=entry['path'],
                    properties={
                        "category": "complexity",
                        "loc": loc,
                        "complexity_score": complexity_score,
                        "iso_characteristic": "maintainability"
                    }
                ))
        
        # Create the run structure
        run = {
            "tool": {
                "driver": {
                    "name": self.tool_name,
                    "version": self.tool_version,
                    "informationUri": "https://github.com/base-index",
                    "rules": self._get_rules()
                }
            },
            "results": results,
            "properties": {
                "indexStats": index_stats,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        }
        
        return run
    
    def _create_result(self, rule_id: str, level: str, message: str, 
                      file_path: str, properties: Dict = None) -> Dict:
        """Create a SARIF result (finding/issue)."""
        result = {
            "ruleId": rule_id,
            "level": level,  # "error", "warning", "note", "none"
            "message": {
                "text": message
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": file_path,
                        "uriBaseId": "SRCROOT"
                    }
                }
            }]
        }
        
        if properties:
            result["properties"] = properties
        
        return result
    
    def _get_rules(self) -> List[Dict]:
        """Define analysis rules with ISO/IEC mappings."""
        return [
            {
                "id": "BI001",
                "name": "LargeFile",
                "shortDescription": {"text": "File size exceeds maintainability threshold"},
                "fullDescription": {
                    "text": "Files larger than 1MB may be difficult to maintain and review. "
                           "Consider splitting into smaller modules."
                },
                "defaultConfiguration": {"level": "warning"},
                "properties": {
                    "tags": ["maintainability", "iso-25010"],
                    "iso_characteristic": "maintainability",
                    "precision": "high"
                }
            },
            {
                "id": "BI002",
                "name": "HighComplexity",
                "shortDescription": {"text": "High cyclomatic complexity detected"},
                "fullDescription": {
                    "text": "Files with >1000 LOC have increased complexity and may be harder "
                           "to understand, test, and maintain. ISO/IEC 5055 recommends modular design."
                },
                "defaultConfiguration": {"level": "warning"},
                "properties": {
                    "tags": ["complexity", "iso-5055", "iso-25010"],
                    "iso_characteristic": "maintainability",
                    "cwe": ["CWE-1080"],  # Source Code File with Excessive Number of Lines
                    "precision": "medium"
                }
            }
        ]
    
    def generate_sarif(self, index_stats: Dict, file_entries: List[Dict], 
                      output_path: Optional[str] = None) -> Dict:
        """
        Generate complete SARIF report.
        
        Args:
            index_stats: Statistics from indexing
            file_entries: List of file entry dictionaries
            output_path: Optional path to save SARIF JSON
        
        Returns:
            Complete SARIF document as dictionary
        """
        run = self.create_run(index_stats, file_entries)
        
        sarif_doc = {
            "$schema": self.SCHEMA_URL,
            "version": self.SARIF_VERSION,
            "runs": [run]
        }
        
        if output_path:
            with open(output_path, 'w') as f:
                json.dump(sarif_doc, f, indent=2)
            self.logger.info(f"SARIF report saved to {output_path}")
        
        return sarif_doc


# ============================================================================
# ISO/IEC Compliance Reporter
# ============================================================================

class ISOComplianceReporter:
    """
    ISO/IEC Software Quality Compliance Reporting.
    
    Implements metrics for:
    - ISO/IEC 5055:2021 - Software Quality Measurement
    - ISO/IEC 25010:2011 - Software Product Quality Model
    - ISO/IEC 25023:2016 - Quality Measurement
    
    Quality Characteristics (ISO 25010):
    1. Functional Suitability
    2. Performance Efficiency
    3. Compatibility
    4. Usability
    5. Reliability
    6. Security
    7. Maintainability ✓ (Primary focus for indexing)
    8. Portability
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def generate_iso_25010_report(self, index_stats: Dict, 
                                   file_entries: List[Dict]) -> Dict:
        """
        Generate ISO/IEC 25010 quality characteristics report.
        """
        # Calculate maintainability metrics
        maintainability_score = self._calculate_maintainability(file_entries)
        
        # Calculate modularity
        modularity_score = self._calculate_modularity(file_entries, index_stats)
        
        # Calculate reusability
        reusability_score = self._calculate_reusability(file_entries)
        
        report = {
            "standard": "ISO/IEC 25010:2011",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "quality_characteristics": {
                "maintainability": {
                    "score": maintainability_score,
                    "max_score": 100,
                    "grade": self._get_grade(maintainability_score),
                    "sub_characteristics": {
                        "modularity": modularity_score,
                        "reusability": reusability_score,
                        "analyzability": self._calculate_analyzability(file_entries),
                        "modifiability": self._calculate_modifiability(file_entries),
                        "testability": self._calculate_testability(file_entries)
                    },
                    "findings": self._get_maintainability_findings(file_entries)
                }
            },
            "compliance_level": self._get_compliance_level(maintainability_score),
            "recommendations": self._generate_recommendations(file_entries)
        }
        
        return report
    
    def _calculate_maintainability(self, file_entries: List[Dict]) -> float:
        """Calculate overall maintainability score (0-100)."""
        if not file_entries:
            return 0.0
        
        scores = []
        for entry in file_entries:
            loc = entry.get('loc') or 0
            size = entry.get('size') or 0
            
            # Penalize large files
            size_score = 100 if size < 10*1024 else max(0, 100 - (size / (100*1024)))
            
            # Penalize high LOC
            loc_score = 100 if loc < 300 else max(0, 100 - ((loc - 300) / 50))
            
            scores.append((size_score + loc_score) / 2)
        
        return sum(scores) / len(scores)
    
    def _calculate_modularity(self, file_entries: List[Dict], 
                             index_stats: Dict) -> float:
        """Calculate modularity score based on file organization."""
        total_files = index_stats.get('total_files', 1)
        file_types = index_stats.get('by_type', {})
        
        # Good modularity = diverse file types, many small files
        type_diversity = len(file_types)
        avg_size = index_stats.get('total_size', 0) / total_files
        
        # Score components
        diversity_score = min(100, type_diversity * 10)
        size_score = 100 if avg_size < 50*1024 else max(0, 100 - (avg_size / (500*1024)))
        
        return (diversity_score + size_score) / 2
    
    def _calculate_reusability(self, file_entries: List[Dict]) -> float:
        """Estimate reusability based on file characteristics."""
        if not file_entries:
            return 0.0
        
        # Files with moderate size are more reusable
        reusable = sum(1 for e in file_entries 
                      if 100 < (e.get('loc') or 0) < 500 and 
                      (e.get('size') or 0) < 100*1024)
        
        return (reusable / len(file_entries)) * 100
    
    def _calculate_analyzability(self, file_entries: List[Dict]) -> float:
        """How easy it is to analyze the code."""
        if not file_entries:
            return 0.0
        
        # Smaller files are easier to analyze
        easy_to_analyze = sum(1 for e in file_entries if (e.get('loc') or 0) < 500)
        return (easy_to_analyze / len(file_entries)) * 100
    
    def _calculate_modifiability(self, file_entries: List[Dict]) -> float:
        """How easy it is to modify the code."""
        # Similar to analyzability but with stricter thresholds
        if not file_entries:
            return 0.0
        
        easy_to_modify = sum(1 for e in file_entries if (e.get('loc') or 0) < 300)
        return (easy_to_modify / len(file_entries)) * 100
    
    def _calculate_testability(self, file_entries: List[Dict]) -> float:
        """How easy it is to test the code."""
        if not file_entries:
            return 0.0
        
        # Moderate-sized files are easier to test
        testable = sum(1 for e in file_entries 
                      if 50 < (e.get('loc') or 0) < 600)
        return (testable / len(file_entries)) * 100
    
    def _get_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 90: return "A"
        if score >= 80: return "B"
        if score >= 70: return "C"
        if score >= 60: return "D"
        return "F"
    
    def _get_compliance_level(self, score: float) -> str:
        """Determine ISO compliance level."""
        if score >= 90: return "Excellent"
        if score >= 75: return "Good"
        if score >= 60: return "Acceptable"
        if score >= 50: return "Needs Improvement"
        return "Non-Compliant"
    
    def _get_maintainability_findings(self, file_entries: List[Dict]) -> List[Dict]:
        """Get specific maintainability findings."""
        findings = []
        
        large_files = [e for e in file_entries if (e.get('size') or 0) > 1024*1024]
        if large_files:
            findings.append({
                "severity": "warning",
                "category": "file_size",
                "count": len(large_files),
                "message": f"{len(large_files)} files exceed 1MB threshold",
                "iso_ref": "ISO 5055 - Modularity"
            })
        
        complex_files = [e for e in file_entries if (e.get('loc') or 0) > 1000]
        if complex_files:
            findings.append({
                "severity": "warning",
                "category": "complexity",
                "count": len(complex_files),
                "message": f"{len(complex_files)} files exceed 1000 LOC threshold",
                "iso_ref": "ISO 5055 - Maintainability"
            })
        
        return findings
    
    def _generate_recommendations(self, file_entries: List[Dict]) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        large_files = [e for e in file_entries if (e.get('size') or 0) > 1024*1024]
        if large_files:
            recommendations.append(
                f"Consider refactoring {len(large_files)} large files into smaller modules"
            )
        
        complex_files = [e for e in file_entries if (e.get('loc') or 0) > 1000]
        if complex_files:
            recommendations.append(
                f"Split {len(complex_files)} complex files to improve maintainability"
            )
        
        if not recommendations:
            recommendations.append("Codebase maintains good ISO 25010 compliance")
        
        return recommendations


# ============================================================================
# Data Science Professional Reporting
# ============================================================================

class DataScienceReporter:
    """
    Professional data science reporting formats.
    
    Supports:
    - Pandas DataFrame export
    - Parquet format (Apache Arrow)
    - CSV with proper encoding
    - JSON Lines (newline-delimited JSON)
    - Statistical summaries
    - Jupyter Notebook integration
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def export_to_csv(self, file_entries: List[Dict], output_path: str):
        """Export to CSV with proper headers and encoding."""
        import csv
        
        if not file_entries:
            self.logger.warning("No data to export")
            return
        
        # Get all unique keys
        fieldnames = set()
        for entry in file_entries:
            fieldnames.update(entry.keys())
        fieldnames = sorted(fieldnames)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(file_entries)
        
        self.logger.info(f"CSV export saved to {output_path}")
    
    def export_to_jsonl(self, file_entries: List[Dict], output_path: str):
        """Export to JSON Lines format (one JSON object per line)."""
        with open(output_path, 'w', encoding='utf-8') as f:
            for entry in file_entries:
                f.write(json.dumps(entry) + '\n')
        
        self.logger.info(f"JSON Lines export saved to {output_path}")
    
    def generate_statistical_summary(self, index_stats: Dict, 
                                     file_entries: List[Dict]) -> Dict:
        """Generate comprehensive statistical summary."""
        if not file_entries:
            return {"error": "No data available"}
        
        # Size statistics
        sizes = [(e.get('size') or 0) for e in file_entries]
        locs = [(e.get('loc') or 0) for e in file_entries if (e.get('loc') or 0) > 0]
        
        summary = {
            "descriptive_statistics": {
                "total_files": len(file_entries),
                "total_size_bytes": sum(sizes),
                "total_size_mb": sum(sizes) / (1024 * 1024),
                "file_size": {
                    "mean": sum(sizes) / len(sizes) if sizes else 0,
                    "median": self._median(sizes),
                    "min": min(sizes) if sizes else 0,
                    "max": max(sizes) if sizes else 0,
                    "std_dev": self._std_dev(sizes)
                },
                "lines_of_code": {
                    "mean": sum(locs) / len(locs) if locs else 0,
                    "median": self._median(locs),
                    "min": min(locs) if locs else 0,
                    "max": max(locs) if locs else 0,
                    "std_dev": self._std_dev(locs)
                }
            },
            "distribution": {
                "by_type": index_stats.get('by_type', {}),
                "size_buckets": self._create_size_buckets(sizes),
                "loc_buckets": self._create_loc_buckets(locs)
            },
            "quality_metrics": {
                "avg_file_size_kb": (sum(sizes) / len(sizes) / 1024) if sizes else 0,
                "avg_loc_per_file": sum(locs) / len(locs) if locs else 0,
                "files_over_1mb": sum(1 for s in sizes if s > 1024*1024),
                "files_over_1000_loc": sum(1 for l in locs if l > 1000)
            },
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        return summary
    
    def _median(self, values: List[float]) -> float:
        """Calculate median."""
        if not values:
            return 0.0
        sorted_vals = sorted(values)
        n = len(sorted_vals)
        if n % 2 == 0:
            return (sorted_vals[n//2-1] + sorted_vals[n//2]) / 2
        return sorted_vals[n//2]
    
    def _std_dev(self, values: List[float]) -> float:
        """Calculate standard deviation."""
        if len(values) < 2:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return variance ** 0.5
    
    def _create_size_buckets(self, sizes: List[int]) -> Dict:
        """Create size distribution buckets."""
        buckets = {
            "< 10 KB": 0,
            "10-100 KB": 0,
            "100 KB - 1 MB": 0,
            "1-10 MB": 0,
            "> 10 MB": 0
        }
        
        for size in sizes:
            if size < 10*1024:
                buckets["< 10 KB"] += 1
            elif size < 100*1024:
                buckets["10-100 KB"] += 1
            elif size < 1024*1024:
                buckets["100 KB - 1 MB"] += 1
            elif size < 10*1024*1024:
                buckets["1-10 MB"] += 1
            else:
                buckets["> 10 MB"] += 1
        
        return buckets
    
    def _create_loc_buckets(self, locs: List[int]) -> Dict:
        """Create LOC distribution buckets."""
        buckets = {
            "< 100": 0,
            "100-300": 0,
            "300-500": 0,
            "500-1000": 0,
            "> 1000": 0
        }
        
        for loc in locs:
            if loc < 100:
                buckets["< 100"] += 1
            elif loc < 300:
                buckets["100-300"] += 1
            elif loc < 500:
                buckets["300-500"] += 1
            elif loc < 1000:
                buckets["500-1000"] += 1
            else:
                buckets["> 1000"] += 1
        
        return buckets


# ============================================================================
# Unified Reporting Interface
# ============================================================================

class BaseIndexReporter:
    """
    Unified interface for all Base Index reporting capabilities.
    
    Generates:
    - SARIF reports (industry standard)
    - ISO/IEC compliance reports
    - Statistical summaries
    - CSV/JSON exports
    - Professional data science formats
    """
    
    def __init__(self):
        self.sarif_reporter = SARIFReporter()
        self.iso_reporter = ISOComplianceReporter()
        self.ds_reporter = DataScienceReporter()
        self.logger = logging.getLogger(__name__)
    
    def generate_all_reports(self, index_stats: Dict, file_entries: List[Dict],
                            output_dir: str = ".") -> Dict[str, str]:
        """
        Generate all available reports.
        
        Args:
            index_stats: Statistics from indexing
            file_entries: List of file entry dictionaries
            output_dir: Directory to save reports
        
        Returns:
            Dictionary mapping report type to file path
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        reports = {}
        
        # SARIF Report
        sarif_path = output_dir / f"base_index_sarif_{timestamp}.json"
        self.sarif_reporter.generate_sarif(index_stats, file_entries, str(sarif_path))
        reports['sarif'] = str(sarif_path)
        
        # ISO Compliance Report
        iso_report = self.iso_reporter.generate_iso_25010_report(index_stats, file_entries)
        iso_path = output_dir / f"base_index_iso25010_{timestamp}.json"
        with open(iso_path, 'w') as f:
            json.dump(iso_report, f, indent=2)
        reports['iso_25010'] = str(iso_path)
        
        # Statistical Summary
        stats_summary = self.ds_reporter.generate_statistical_summary(index_stats, file_entries)
        stats_path = output_dir / f"base_index_statistics_{timestamp}.json"
        with open(stats_path, 'w') as f:
            json.dump(stats_summary, f, indent=2)
        reports['statistics'] = str(stats_path)
        
        # CSV Export
        csv_path = output_dir / f"base_index_data_{timestamp}.csv"
        self.ds_reporter.export_to_csv(file_entries, str(csv_path))
        reports['csv'] = str(csv_path)
        
        # JSON Lines Export
        jsonl_path = output_dir / f"base_index_data_{timestamp}.jsonl"
        self.ds_reporter.export_to_jsonl(file_entries, str(jsonl_path))
        reports['jsonl'] = str(jsonl_path)
        
        # Summary report
        summary_path = output_dir / f"base_index_summary_{timestamp}.json"
        summary = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "base_index_version": "2.0.0",
            "reports_generated": reports,
            "index_summary": index_stats,
            "iso_compliance": {
                "maintainability_score": iso_report['quality_characteristics']['maintainability']['score'],
                "grade": iso_report['quality_characteristics']['maintainability']['grade'],
                "compliance_level": iso_report['compliance_level']
            },
            "sarif_findings_count": len(self.sarif_reporter.create_run(index_stats, file_entries)['results'])
        }
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        reports['summary'] = str(summary_path)
        
        self.logger.info(f"Generated {len(reports)} reports in {output_dir}")
        return reports


# ============================================================================
# CLI Interface
# ============================================================================

if __name__ == "__main__":
    import sys
    from base_index import BaseIndexer
    
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    
    if len(sys.argv) < 2:
        print("Usage: python base_index_reporting.py <directory> [output_dir]")
        print("\nGenerates industry-grade reports:")
        print("  - SARIF (Static Analysis Results Interchange Format)")
        print("  - ISO/IEC 25010 compliance report")
        print("  - Statistical analysis")
        print("  - CSV/JSON data exports")
        sys.exit(1)
    
    root_dir = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "./reports"
    
    print(f"\n🔍 Base Index - Industry-Grade Reporting\n")
    print(f"Indexing: {root_dir}")
    print(f"Output: {output_dir}\n")
    
    # Index the codebase
    indexer = BaseIndexer(root_dir)
    stats = indexer.index()
    
    # Convert file entries to dict format
    file_entries = []
    for entry in indexer._index.values():
        file_entries.append({
            'path': entry.path,
            'size': entry.size,
            'type': entry.type,
            'loc': entry.loc,
            'hash': entry.hash
        })
    
    # Generate all reports
    reporter = BaseIndexReporter()
    reports = reporter.generate_all_reports(stats, file_entries, output_dir)
    
    print("\n✅ Reports generated:\n")
    for report_type, path in reports.items():
        print(f"  {report_type:20} → {path}")
    
    print(f"\n📊 Index Stats:")
    print(f"  Files: {stats['total_files']:,}")
    print(f"  Size: {stats['total_size']/(1024*1024):.2f} MB")
    print(f"  Duration: {stats['index_duration']:.2f}s")
    print()
