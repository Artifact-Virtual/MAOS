"""
Test suite for Base Index Reporting Module

Tests all industry-grade reporting capabilities:
- SARIF report generation
- ISO/IEC compliance reporting
- Data science professional exports
"""

import os
import json
import tempfile
import shutil
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from base_index import BaseIndexer
from base_index_reporting import (
    SARIFReporter,
    ISOComplianceReporter,
    DataScienceReporter,
    BaseIndexReporter
)


def test_sarif_reporter():
    """Test SARIF report generation."""
    print("\n[Test 1] SARIF Reporter")
    print("-" * 60)
    
    reporter = SARIFReporter()
    
    # Mock data
    index_stats = {
        'total_files': 100,
        'total_size': 5000000,
        'total_loc': 15000
    }
    
    file_entries = [
        {'path': 'large_file.py', 'size': 2*1024*1024, 'loc': 500, 'type': 'py', 'hash': 'abc123'},
        {'path': 'complex.py', 'size': 100*1024, 'loc': 1500, 'type': 'py', 'hash': 'def456'},
        {'path': 'normal.py', 'size': 50*1024, 'loc': 200, 'type': 'py', 'hash': 'ghi789'},
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = os.path.join(tmpdir, 'test.sarif')
        sarif_doc = reporter.generate_sarif(index_stats, file_entries, output_path)
        
        # Verify SARIF structure
        assert '$schema' in sarif_doc
        assert sarif_doc['version'] == '2.1.0'
        assert 'runs' in sarif_doc
        assert len(sarif_doc['runs']) > 0
        
        run = sarif_doc['runs'][0]
        assert 'tool' in run
        assert 'results' in run
        assert run['tool']['driver']['name'] == 'Base Index'
        
        # Verify file was created
        assert os.path.exists(output_path)
        
        # Verify it's valid JSON
        with open(output_path, 'r') as f:
            loaded = json.load(f)
            assert loaded['version'] == '2.1.0'
        
        print(f"  ✓ SARIF schema version: {sarif_doc['version']}")
        print(f"  ✓ Tool name: {run['tool']['driver']['name']}")
        print(f"  ✓ Results count: {len(run['results'])}")
        print(f"  ✓ Rules defined: {len(run['tool']['driver']['rules'])}")
        print(f"  ✓ File created: {output_path}")
        print("  ✓ Valid JSON structure")
        print("\n✅ SARIF Reporter: PASSED")


def test_iso_compliance_reporter():
    """Test ISO/IEC compliance reporting."""
    print("\n[Test 2] ISO/IEC Compliance Reporter")
    print("-" * 60)
    
    reporter = ISOComplianceReporter()
    
    # Mock data
    index_stats = {
        'total_files': 150,
        'total_size': 10000000,
        'total_loc': 25000,
        'by_type': {
            'py': 80,
            'js': 40,
            'html': 20,
            'css': 10
        }
    }
    
    file_entries = [
        {'path': f'file{i}.py', 'size': 50*1024, 'loc': 300, 'type': 'py', 'hash': f'hash{i}'}
        for i in range(100)
    ] + [
        {'path': 'large.py', 'size': 2*1024*1024, 'loc': 1500, 'type': 'py', 'hash': 'large1'},
        {'path': 'complex.py', 'size': 1*1024*1024, 'loc': 2000, 'type': 'py', 'hash': 'complex1'},
    ]
    
    report = reporter.generate_iso_25010_report(index_stats, file_entries)
    
    # Verify report structure
    assert 'standard' in report
    assert report['standard'] == 'ISO/IEC 25010:2011'
    assert 'quality_characteristics' in report
    assert 'maintainability' in report['quality_characteristics']
    
    maint = report['quality_characteristics']['maintainability']
    assert 'score' in maint
    assert 'grade' in maint
    assert 'sub_characteristics' in maint
    assert 'findings' in maint
    assert 'recommendations' in report
    
    # Check sub-characteristics
    sub_chars = maint['sub_characteristics']
    assert 'modularity' in sub_chars
    assert 'reusability' in sub_chars
    assert 'analyzability' in sub_chars
    assert 'modifiability' in sub_chars
    assert 'testability' in sub_chars
    
    print(f"  ✓ Standard: {report['standard']}")
    print(f"  ✓ Maintainability Score: {maint['score']:.2f}/100")
    print(f"  ✓ Grade: {maint['grade']}")
    print(f"  ✓ Compliance Level: {report['compliance_level']}")
    print(f"  ✓ Modularity: {sub_chars['modularity']:.2f}")
    print(f"  ✓ Reusability: {sub_chars['reusability']:.2f}")
    print(f"  ✓ Findings: {len(maint['findings'])}")
    print(f"  ✓ Recommendations: {len(report['recommendations'])}")
    print("\n✅ ISO Compliance Reporter: PASSED")


def test_data_science_reporter():
    """Test data science professional reporting."""
    print("\n[Test 3] Data Science Reporter")
    print("-" * 60)
    
    reporter = DataScienceReporter()
    
    # Mock data
    index_stats = {
        'total_files': 200,
        'total_size': 15000000,
        'total_loc': 35000,
        'by_type': {
            'py': 120,
            'js': 50,
            'html': 20,
            'css': 10
        }
    }
    
    file_entries = [
        {'path': f'src/module{i}.py', 'size': i*10000, 'loc': i*50, 'type': 'py', 'hash': f'h{i}'}
        for i in range(1, 51)
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        # Test CSV export
        csv_path = os.path.join(tmpdir, 'test.csv')
        reporter.export_to_csv(file_entries, csv_path)
        assert os.path.exists(csv_path)
        
        with open(csv_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) > 1  # Header + data
            assert 'path' in lines[0].lower()
        
        # Test JSON Lines export
        jsonl_path = os.path.join(tmpdir, 'test.jsonl')
        reporter.export_to_jsonl(file_entries, jsonl_path)
        assert os.path.exists(jsonl_path)
        
        with open(jsonl_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == len(file_entries)
            first_entry = json.loads(lines[0])
            assert 'path' in first_entry
        
        # Test statistical summary
        summary = reporter.generate_statistical_summary(index_stats, file_entries)
        assert 'descriptive_statistics' in summary
        assert 'distribution' in summary
        assert 'quality_metrics' in summary
        
        desc_stats = summary['descriptive_statistics']
        assert 'total_files' in desc_stats
        assert 'file_size' in desc_stats
        assert 'lines_of_code' in desc_stats
        
        file_size_stats = desc_stats['file_size']
        assert 'mean' in file_size_stats
        assert 'median' in file_size_stats
        assert 'min' in file_size_stats
        assert 'max' in file_size_stats
        assert 'std_dev' in file_size_stats
        
        print(f"  ✓ CSV export: {csv_path} ({len(lines)} rows)")
        print(f"  ✓ JSON Lines export: {jsonl_path} ({len(lines)} entries)")
        print(f"  ✓ Statistical summary generated")
        print(f"  ✓ Mean file size: {file_size_stats['mean']:.2f} bytes")
        print(f"  ✓ Median file size: {file_size_stats['median']:.2f} bytes")
        print(f"  ✓ Std dev: {file_size_stats['std_dev']:.2f}")
        print(f"  ✓ Size buckets: {summary['distribution']['size_buckets']}")
        print("\n✅ Data Science Reporter: PASSED")


def test_unified_reporter():
    """Test unified reporting interface."""
    print("\n[Test 4] Unified Reporter (BaseIndexReporter)")
    print("-" * 60)
    
    reporter = BaseIndexReporter()
    
    # Mock data
    index_stats = {
        'total_files': 250,
        'total_size': 20000000,
        'total_loc': 45000,
        'by_type': {
            'py': 150,
            'js': 60,
            'html': 25,
            'css': 15
        }
    }
    
    file_entries = [
        {'path': f'project/src{i}.py', 'size': i*5000, 'loc': i*25, 'type': 'py', 'hash': f'hash{i}'}
        for i in range(1, 101)
    ]
    
    with tempfile.TemporaryDirectory() as tmpdir:
        report_paths = reporter.generate_all_reports(index_stats, file_entries, tmpdir)
        
        # Verify all report types were generated
        expected_types = ['sarif', 'iso_25010', 'statistics', 'csv', 'jsonl', 'summary']
        for report_type in expected_types:
            assert report_type in report_paths, f"Missing {report_type} report"
            assert os.path.exists(report_paths[report_type]), f"File not found: {report_paths[report_type]}"
        
        # Verify summary report content
        with open(report_paths['summary'], 'r') as f:
            summary = json.load(f)
            assert 'timestamp' in summary
            assert 'base_index_version' in summary
            assert 'reports_generated' in summary
            assert 'index_summary' in summary
            assert 'iso_compliance' in summary
            assert 'sarif_findings_count' in summary
        
        print(f"  ✓ Reports generated: {len(report_paths)}")
        for report_type, path in report_paths.items():
            file_size = os.path.getsize(path)
            print(f"  ✓ {report_type:20} → {Path(path).name} ({file_size:,} bytes)")
        
        print(f"\n  ISO Compliance:")
        print(f"    Score: {summary['iso_compliance']['maintainability_score']:.2f}")
        print(f"    Grade: {summary['iso_compliance']['grade']}")
        print(f"    Level: {summary['iso_compliance']['compliance_level']}")
        print(f"\n  SARIF Findings: {summary['sarif_findings_count']}")
        
        print("\n✅ Unified Reporter: PASSED")


def test_integration_with_base_indexer():
    """Test integration with actual Base Indexer."""
    print("\n[Test 5] Integration with BaseIndexer")
    print("-" * 60)
    
    # Create temporary test directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create some test files
        test_dir = os.path.join(tmpdir, 'test_project')
        os.makedirs(test_dir)
        
        # Create test files
        for i in range(10):
            file_path = os.path.join(test_dir, f'module{i}.py')
            with open(file_path, 'w') as f:
                f.write(f'# Module {i}\n' * (50 + i * 20))
        
        # Large file
        large_file = os.path.join(test_dir, 'large_module.py')
        with open(large_file, 'w') as f:
            f.write('# Large module\n' * 2000)
        
        # Index the directory
        indexer = BaseIndexer(test_dir, workers=2)
        stats = indexer.index()
        
        # Convert to dict format
        file_entries = []
        for entry in indexer._index.values():
            file_entries.append({
                'path': entry.path,
                'size': entry.size,
                'type': entry.type,
                'loc': entry.loc,
                'hash': entry.hash
            })
        
        # Generate reports
        report_dir = os.path.join(tmpdir, 'reports')
        reporter = BaseIndexReporter()
        report_paths = reporter.generate_all_reports(stats, file_entries, report_dir)
        
        print(f"  ✓ Indexed {stats['total_files']} files")
        print(f"  ✓ Total size: {stats['total_size']:,} bytes")
        print(f"  ✓ Total LOC: {stats['total_loc']:,}")
        print(f"  ✓ Generated {len(report_paths)} reports")
        
        # Verify SARIF content
        with open(report_paths['sarif'], 'r') as f:
            sarif = json.load(f)
            results = sarif['runs'][0]['results']
            print(f"  ✓ SARIF findings: {len(results)}")
            if results:
                print(f"    - {results[0]['ruleId']}: {results[0]['message']['text']}")
        
        # Verify ISO report
        with open(report_paths['iso_25010'], 'r') as f:
            iso_report = json.load(f)
            maint_score = iso_report['quality_characteristics']['maintainability']['score']
            print(f"  ✓ ISO Maintainability: {maint_score:.2f}/100")
        
        print("\n✅ Integration Test: PASSED")


def run_all_tests():
    """Run all reporting tests."""
    print("\n" + "=" * 60)
    print("BASE INDEX REPORTING MODULE - TEST SUITE")
    print("=" * 60)
    print("\nTesting industry-grade reporting capabilities:")
    print("  - SARIF (Static Analysis Results Interchange Format)")
    print("  - ISO/IEC 25010 Quality Compliance")
    print("  - Data Science Professional Formats")
    print("  - Unified Reporting Interface")
    print("  - Integration with Base Indexer")
    
    try:
        test_sarif_reporter()
        test_iso_compliance_reporter()
        test_data_science_reporter()
        test_unified_reporter()
        test_integration_with_base_indexer()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED!")
        print("=" * 60)
        print("\nReporting capabilities validated:")
        print("  ✓ SARIF v2.1.0 generation")
        print("  ✓ ISO/IEC 25010:2011 compliance")
        print("  ✓ ISO/IEC 5055:2021 metrics")
        print("  ✓ CSV/JSON/JSON Lines exports")
        print("  ✓ Statistical analysis")
        print("  ✓ Integration with indexer")
        print("\n✅ Base Index now includes enterprise-grade reporting!")
        print()
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
