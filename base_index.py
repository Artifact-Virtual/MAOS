"""
Base Index Enhanced Indexing Module - Standalone, Production-Ready

A compact, high-performance indexing module designed for:
- Extremely large codebases (millions of files)
- Big data processing
- Easy integration with any automation system
- Zero external dependencies (except stdlib)

Features:
✓ Incremental indexing (only process changed files)
✓ Parallel processing (multi-threaded)
✓ Memory-efficient chunked processing
✓ Persistent index storage
✓ Content hashing for change detection
✓ Comprehensive statistics and reporting
✓ Smart ignore patterns
✓ Export capabilities (JSON, CSV)

Usage:
    from base_index import BaseIndexer
    
    indexer = BaseIndexer("/path/to/codebase")
    stats = indexer.index()
    print(f"Indexed {stats['total_files']} files in {stats['index_duration']:.2f}s")
"""

__version__ = "2.0.0"
__author__ = "Base Index Team"

import os
import hashlib
import json
import pickle
import logging
import threading
from pathlib import Path
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, asdict
from fnmatch import fnmatch


# ============================================================================
# Core Data Structures
# ============================================================================

@dataclass
class FileEntry:
    """Minimal file metadata for efficient storage."""
    path: str
    size: int
    mtime: float
    hash: Optional[str]
    type: str
    loc: Optional[int] = None  # lines of code
    
    def to_dict(self) -> Dict:
        return asdict(self)


# ============================================================================
# Main Indexer Class
# ============================================================================

class BaseIndexer:
    """
    Standalone, production-grade code indexer.
    
    Design goals:
    - Handle codebases with millions of files
    - Memory-efficient (chunked processing)
    - Fast (parallel processing, incremental updates)
    - Reliable (persistent storage, error recovery)
    - Simple API (easy integration)
    """
    
    # Standard ignore patterns
    IGNORE_PATTERNS = [
        'venv', '__pycache__', '.git', '.svn', '.hg',
        '.idea', '.vscode', '.vs', '.DS_Store',
        '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.dylib',
        '*.swp', '*.swo', '*.log', '*.tmp', '*.bak', '*.cache',
        'node_modules', 'bower_components', 'dist', 'build',
        'target', 'bin', 'obj', 'out', '.next', '.nuxt',
        '*.min.js', '*.min.css', '*.map', 'coverage',
        '.mypy_cache', '.pytest_cache', '.tox', '.eggs',
    ]
    
    def __init__(
        self,
        root_dir: str,
        workers: int = 4,
        chunk_size: int = 1000,
        max_file_size: int = 10 * 1024 * 1024,
        enable_hashing: bool = True,
        cache_file: Optional[str] = None,
        ignore_patterns: Optional[List[str]] = None
    ):
        """
        Initialize indexer.
        
        Args:
            root_dir: Root directory to index
            workers: Number of parallel workers
            chunk_size: Files per processing chunk
            max_file_size: Skip files larger than this (bytes)
            enable_hashing: Enable content hashing
            cache_file: Path to persistent cache (default: .maos_cache in root)
            ignore_patterns: Additional patterns to ignore
        """
        self.root = Path(root_dir).resolve()
        self.workers = workers
        self.chunk_size = chunk_size
        self.max_file_size = max_file_size
        self.enable_hashing = enable_hashing
        
        self.cache_file = cache_file or str(self.root / '.maos_index_cache')
        
        self.patterns = self.IGNORE_PATTERNS.copy()
        if ignore_patterns:
            self.patterns.extend(ignore_patterns)
        
        self._index: Dict[str, FileEntry] = {}
        self.stats = {
            'total_files': 0,
            'total_size': 0,
            'total_loc': 0,
            'added': 0,
            'modified': 0,
            'removed': 0,
            'skipped': 0,
            'duration': 0,
        }
        
        self.logger = logging.getLogger('BaseIndexer')
        self._load_cache()
    
    def _should_ignore(self, path: Path) -> bool:
        """Check if path matches ignore patterns."""
        path_str = str(path)
        for part in path.parts:
            for pattern in self.patterns:
                if fnmatch(part, pattern):
                    return True
        for pattern in self.patterns:
            if fnmatch(path_str, pattern) or fnmatch(path.name, pattern):
                return True
        return False
    
    def _hash_file(self, path: Path) -> Optional[str]:
        """Compute SHA256 hash of file content."""
        if not self.enable_hashing or path.stat().st_size > self.max_file_size:
            return None
        try:
            h = hashlib.sha256()
            with open(path, 'rb') as f:
                while chunk := f.read(8192):
                    h.update(chunk)
            return h.hexdigest()[:16]  # Use first 16 chars for efficiency
        except:
            return None
    
    def _detect_type(self, name: str) -> str:
        """Detect file type from extension."""
        ext = os.path.splitext(name)[1].lower()
        types = {
            '.py': 'python', '.js': 'js', '.ts': 'ts', '.java': 'java',
            '.cpp': 'cpp', '.c': 'c', '.go': 'go', '.rs': 'rust',
            '.rb': 'ruby', '.php': 'php', '.sh': 'sh', '.ps1': 'ps',
            '.md': 'doc', '.txt': 'doc', '.rst': 'doc',
            '.json': 'data', '.yaml': 'data', '.yml': 'data',
            '.xml': 'data', '.csv': 'data', '.toml': 'data',
        }
        return types.get(ext, 'other')
    
    def _count_loc(self, path: Path) -> Optional[int]:
        """Count lines in text files."""
        try:
            if path.stat().st_size > self.max_file_size:
                return None
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return sum(1 for _ in f)
        except:
            return None
    
    def _process_file(self, path: Path) -> Optional[FileEntry]:
        """Process single file and return metadata."""
        try:
            rel = path.relative_to(self.root)
            if self._should_ignore(rel):
                return None
            
            stat = path.stat()
            if stat.st_size > self.max_file_size:
                self.stats['skipped'] += 1
                return None
            
            rel_str = str(rel)
            
            # Incremental: skip if unchanged
            if rel_str in self._index:
                old = self._index[rel_str]
                if old.mtime == stat.st_mtime:
                    return old
            
            ftype = self._detect_type(path.name)
            fhash = self._hash_file(path)
            loc = self._count_loc(path) if ftype in ['python', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rust'] else None
            
            entry = FileEntry(
                path=rel_str,
                size=stat.st_size,
                mtime=stat.st_mtime,
                hash=fhash,
                type=ftype,
                loc=loc
            )
            
            if rel_str not in self._index:
                self.stats['added'] += 1
            else:
                self.stats['modified'] += 1
            
            return entry
        except Exception as e:
            self.logger.debug(f"Error processing {path}: {e}")
            return None
    
    def _collect_files(self) -> List[Path]:
        """Collect all files to process."""
        files = []
        for root, dirs, names in os.walk(self.root):
            dirs[:] = [d for d in dirs if not self._should_ignore(Path(root) / d)]
            files.extend(Path(root) / n for n in names)
        return files
    
    def _process_chunk(self, files: List[Path]) -> List[FileEntry]:
        """Process chunk of files in parallel."""
        results = []
        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            futures = {executor.submit(self._process_file, f): f for f in files}
            for future in as_completed(futures):
                try:
                    entry = future.result()
                    if entry:
                        results.append(entry)
                except Exception as e:
                    self.logger.error(f"Error: {e}")
        return results
    
    def index(self) -> Dict:
        """
        Run indexing process.
        
        Returns:
            Statistics dictionary
        """
        start = datetime.now()
        self.logger.info(f"Starting index: {self.root}")
        
        # Reset stats
        self.stats.update({'added': 0, 'modified': 0, 'removed': 0, 'skipped': 0})
        
        # Collect files
        files = self._collect_files()
        self.logger.info(f"Found {len(files)} files")
        
        # Process in chunks
        new_index = {}
        total_chunks = (len(files) + self.chunk_size - 1) // self.chunk_size
        
        for i in range(0, len(files), self.chunk_size):
            chunk = files[i:i + self.chunk_size]
            chunk_num = i // self.chunk_size + 1
            self.logger.info(f"Processing chunk {chunk_num}/{total_chunks}")
            
            entries = self._process_chunk(chunk)
            for entry in entries:
                new_index[entry.path] = entry
        
        # Detect removals
        old_paths = set(self._index.keys())
        new_paths = set(new_index.keys())
        self.stats['removed'] = len(old_paths - new_paths)
        
        # Update index
        self._index = new_index
        
        # Update stats
        self.stats['total_files'] = len(self._index)
        self.stats['total_size'] = sum(e.size for e in self._index.values())
        self.stats['total_loc'] = sum(e.loc or 0 for e in self._index.values())
        self.stats['duration'] = (datetime.now() - start).total_seconds()
        
        self._save_cache()
        
        self.logger.info(
            f"Complete: {self.stats['total_files']} files, "
            f"{self.stats['total_size']/(1024*1024):.1f}MB, "
            f"{self.stats['total_loc']} LOC in {self.stats['duration']:.2f}s"
        )
        
        return self.stats.copy()
    
    def _save_cache(self):
        """Save index to persistent cache."""
        try:
            with open(self.cache_file, 'wb') as f:
                pickle.dump({'index': self._index, 'stats': self.stats}, f)
        except Exception as e:
            self.logger.error(f"Cache save failed: {e}")
    
    def _load_cache(self):
        """Load index from cache if available."""
        try:
            if Path(self.cache_file).exists():
                with open(self.cache_file, 'rb') as f:
                    data = pickle.load(f)
                    self._index = data.get('index', {})
                    self.stats = data.get('stats', self.stats)
                self.logger.info(f"Loaded cache: {len(self._index)} files")
        except Exception as e:
            self.logger.debug(f"No cache loaded: {e}")
    
    def export_json(self, path: str):
        """Export index to JSON."""
        data = {
            'stats': self.stats,
            'files': [e.to_dict() for e in self._index.values()]
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def export_csv(self, path: str):
        """Export index to CSV."""
        import csv
        with open(path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=['path', 'size', 'type', 'loc'])
            writer.writeheader()
            for e in self._index.values():
                writer.writerow({'path': e.path, 'size': e.size, 'type': e.type, 'loc': e.loc})
    
    def get_by_type(self, ftype: str) -> List[FileEntry]:
        """Get all files of specific type."""
        return [e for e in self._index.values() if e.type == ftype]
    
    def get_largest(self, n: int = 10) -> List[FileEntry]:
        """Get N largest files."""
        return sorted(self._index.values(), key=lambda e: e.size, reverse=True)[:n]
    
    def search(self, pattern: str) -> List[FileEntry]:
        """Search files by path pattern."""
        p = pattern.lower()
        return [e for e in self._index.values() if p in e.path.lower()]
    
    def get_stats(self) -> Dict:
        """Get detailed statistics."""
        types = {}
        for e in self._index.values():
            types[e.type] = types.get(e.type, 0) + 1
        
        return {
            **self.stats,
            'by_type': types,
            'avg_size': self.stats['total_size'] / max(self.stats['total_files'], 1),
        }


# ============================================================================
# Scheduled Indexer (for background operation)
# ============================================================================

class ScheduledBaseIndexer(BaseIndexer):
    """
    Indexer with automatic scheduled updates.
    
    Usage:
        indexer = ScheduledBaseIndexer("/path/to/code", interval=300)
        indexer.start()
        # ... indexer runs in background ...
        indexer.stop()
    """
    
    def __init__(self, root_dir: str, interval: int = 300, **kwargs):
        """
        Args:
            root_dir: Root directory
            interval: Seconds between index updates
            **kwargs: Additional args for BaseIndexer
        """
        super().__init__(root_dir, **kwargs)
        self.interval = interval
        self._stop = threading.Event()
        self._thread = None
    
    def start(self):
        """Start scheduled indexing in background."""
        if self._thread and self._thread.is_alive():
            return
        
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.logger.info(f"Scheduled indexing started ({self.interval}s interval)")
    
    def stop(self):
        """Stop scheduled indexing."""
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=10)
        self.logger.info("Scheduled indexing stopped")
    
    def _run(self):
        """Background indexing loop."""
        while not self._stop.is_set():
            try:
                self.index()
            except Exception as e:
                self.logger.error(f"Index error: {e}")
            
            self._stop.wait(self.interval)


# ============================================================================
# CLI Interface (when run as script)
# ============================================================================

def main():
    """Command-line interface."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Base Index Indexer - Index large codebases")
    parser.add_argument('directory', help='Directory to index')
    parser.add_argument('-w', '--workers', type=int, default=4, help='Number of workers')
    parser.add_argument('-o', '--output', help='Export to JSON file')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format='%(asctime)s - %(name)s - %(message)s'
    )
    
    indexer = BaseIndexer(args.directory, workers=args.workers)
    stats = indexer.index()
    
    print("\n" + "="*60)
    print("INDEXING COMPLETE")
    print("="*60)
    print(f"Total Files:  {stats['total_files']:,}")
    print(f"Total Size:   {stats['total_size']/(1024*1024):.2f} MB")
    print(f"Total LOC:    {stats['total_loc']:,}")
    print(f"Added:        {stats['added']}")
    print(f"Modified:     {stats['modified']}")
    print(f"Removed:      {stats['removed']}")
    print(f"Duration:     {stats['duration']:.2f}s")
    print("="*60)
    
    if args.output:
        indexer.export_json(args.output)
        print(f"Exported to: {args.output}")


if __name__ == '__main__':
    main()
