"""
Index creation utilities for MAOS system.
Provides file scanning and indexing functionality.
"""
import os
from pathlib import Path


def scan_directory(directory, ignore_patterns=None):
    """
    Scan a directory and return information about all files.
    
    Args:
        directory: Root directory to scan
        ignore_patterns: List of patterns to ignore (optional)
        
    Returns:
        List of file information dictionaries
    """
    if ignore_patterns is None:
        ignore_patterns = []
    
    files_info = []
    directory = Path(directory)
    
    for root, dirs, files in os.walk(directory):
        # Filter ignored directories
        dirs[:] = [d for d in dirs if not _should_ignore(d, ignore_patterns)]
        
        for file in files:
            file_path = Path(root) / file
            if _should_ignore(file, ignore_patterns):
                continue
                
            try:
                stat = file_path.stat()
                rel_path = file_path.relative_to(directory)
                
                files_info.append({
                    'path': str(rel_path),
                    'absolute_path': str(file_path),
                    'size': stat.st_size,
                    'last_modified': stat.st_mtime,
                    'type': _detect_file_type(file)
                })
            except Exception as e:
                # Skip files we can't access
                continue
    
    return files_info


def _should_ignore(name, patterns):
    """Check if a file or directory should be ignored."""
    from fnmatch import fnmatch
    
    for pattern in patterns:
        if fnmatch(name, pattern):
            return True
    return False


def _detect_file_type(filename):
    """Detect file type based on extension."""
    ext = os.path.splitext(filename)[1].lower()
    
    if ext in ['.py', '.sh', '.ps1', '.js', '.ts', '.rb', '.go', '.cpp', '.c', '.java']:
        return 'script'
    elif ext in ['.md', '.txt', '.rst']:
        return 'markdown'
    elif ext in ['.ipynb']:
        return 'notebook'
    elif ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.cfg']:
        return 'config'
    elif ext in ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']:
        return 'image'
    else:
        return 'other'
