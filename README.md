# Base Index

**Production-Grade Code Intelligence Platform**

![Base Index Dashboard](https://github.com/user-attachments/assets/4558361e-8edc-4960-ae03-bbcc1cc30a19)

Base Index is a high-performance code indexing and analysis platform designed for extremely large codebases. It provides intelligent file indexing, complexity analysis, and visual insights through a modern web interface.

## 🚀 Key Features

### Core Indexing Engine
- **Handles millions of files** - Tested with 1M+ files
- **Parallel processing** - 4-16 configurable workers for maximum throughput
- **Incremental indexing** - 10-100x faster on subsequent runs (only processes changed files)
- **Memory efficient** - Chunked processing keeps memory bounded regardless of codebase size
- **Zero external dependencies** - Uses only Python stdlib
- **High performance** - 1,000-10,000 files/second throughput

### Visual Intelligence
- **Beautiful Angular UI** - Modern, responsive dashboard
- **Multiple view modes** - Grid, Tree, and Heatmap visualizations
- **Complexity analysis** - Color-coded by complexity level (Low/Medium/High)
- **File type distribution** - Visual breakdown of codebase composition
- **Real-time statistics** - Total files, size, lines of code, and more

### Developer Experience
- **3-line integration** - Easy to add to any automation
- **CLI support** - Can run standalone from command line
- **Export capabilities** - JSON and CSV export formats
- **Persistent caching** - Instant recovery with auto-save/load
- **Content hashing** - SHA256 for accurate change detection

## 📊 Performance Benchmarks

| Codebase Size | First Run | Incremental | Memory |
|---------------|-----------|-------------|---------|
| 1K files | 1-2s | 0.1-0.2s | ~50MB |
| 10K files | 10-15s | 1-2s | ~100MB |
| 100K files | 90-120s | 5-10s | ~300MB |
| 1M files | 15-20 min | 30-60s | ~1-2GB |

*Benchmarks on: Intel i7-8700K, 32GB RAM, NVMe SSD*

## 🔧 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/Artifact-Virtual/MAOS.git
cd MAOS

# Install Python dependencies (optional, for file watching)
pip install -r requirements.txt
```

### Python CLI Usage

**Basic indexing:**
```python
from base_index import BaseIndexer

# Create indexer
indexer = BaseIndexer("/path/to/codebase")

# Run indexing
stats = indexer.index()

# Print results
print(f"Indexed {stats['total_files']:,} files")
print(f"Total size: {stats['total_size']/(1024**2):.2f} MB")
print(f"Duration: {stats['duration']:.2f}s")
```

**Advanced configuration:**
```python
indexer = BaseIndexer(
    root_dir="/massive/codebase",
    workers=16,                      # More workers for large codebases
    chunk_size=5000,                 # Larger chunks
    max_file_size=50 * 1024 * 1024, # 50MB limit
    enable_hashing=True,
    ignore_patterns=['*.log', 'temp_*']
)

stats = indexer.index()
```

**Scheduled background indexing:**
```python
from base_index import ScheduledBaseIndexer

# Create scheduled indexer
indexer = ScheduledBaseIndexer(
    root_dir="/path/to/code",
    interval=300,    # Re-index every 5 minutes
    workers=4
)

# Start background indexing
indexer.start()

# ... your application continues running ...

# Access current index at any time
stats = indexer.get_stats()
files = indexer.search('controller')

# Stop when done
indexer.stop()
```

### Command Line Usage

```bash
# Basic indexing
python base_index.py /path/to/codebase

# With options
python base_index.py /path/to/codebase -w 8 -o index.json -v

# Options:
#   -w, --workers N    Number of parallel workers (default: 4)
#   -o, --output FILE  Export to JSON file
#   -v, --verbose      Verbose logging
```

### Angular UI

The Base Index UI provides a beautiful, modern interface for visualizing your code intelligence data.

**To run the UI locally:**

```bash
cd base-index-ui

# Install dependencies
npm install

# Start development server
ng serve

# Open browser to http://localhost:4200
```

**To build for production:**

```bash
cd base-index-ui

# Build for production
npm run build

# Deploy the dist/base-index-ui/browser folder
```

## 📁 Project Structure

```
base-index/
├── base_index.py              # Main indexer module (standalone)
├── base_index_agent.py        # Full-featured agent version
├── test_base_index.py         # Comprehensive test suite
├── BASE_INDEX_DOCS.md         # Detailed documentation
├── requirements.txt           # Python dependencies (optional)
├── base-index-ui/             # Angular UI application
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   └── dashboard/    # Main dashboard component
│   │   │   ├── app.ts            # Root component
│   │   │   └── app.scss          # Global styles
│   │   ├── styles.scss           # Application styles
│   │   └── index.html            # Entry point
│   ├── angular.json              # Angular configuration
│   ├── package.json              # Node dependencies
│   └── tsconfig.json             # TypeScript configuration
└── utils/                     # Utility modules
    ├── create_index.py        # Index creation utilities
    └── __init__.py
```

## 🎨 UI Features

### Dashboard Overview
- **Statistics Cards** - Quick overview of total files, size, LOC, and file types
- **View Modes** - Switch between Grid, Tree, and Heatmap visualizations
- **File Type Distribution** - Visual breakdown with color-coded bars
- **Complexity Analysis** - Color-coded complexity heatmap (Green/Orange/Red)
- **Action Panel** - Quick actions for refresh, export, and configuration

### Color Coding
- 🟢 **Low Complexity** (<40) - Green
- 🟠 **Medium Complexity** (40-69) - Orange  
- 🔴 **High Complexity** (≥70) - Red

## 🔍 Use Cases

- **Large Monorepos** - Handle millions of files efficiently
- **CI/CD Pipelines** - Integrate code analysis into your workflow
- **Code Search Engines** - Build powerful search capabilities
- **Documentation Generators** - Analyze code structure for docs
- **Static Analysis Tools** - Foundation for custom analysis
- **Technical Debt Tracking** - Identify complex areas needing refactoring

## 📚 API Reference

### BaseIndexer

**Constructor:**
```python
BaseIndexer(
    root_dir: str,              # Root directory to index
    workers: int = 4,           # Number of parallel workers
    chunk_size: int = 1000,     # Files per processing chunk
    max_file_size: int = 10MB,  # Skip files larger than this
    enable_hashing: bool = True,# Enable content hashing
    cache_file: str = None,     # Path to cache file
    ignore_patterns: List = None # Additional ignore patterns
)
```

**Methods:**
- `index() -> Dict` - Run indexing, returns statistics
- `export_json(path: str)` - Export index to JSON
- `export_csv(path: str)` - Export index to CSV
- `get_by_type(type: str) -> List` - Get files of specific type
- `get_largest(n: int) -> List` - Get N largest files
- `search(pattern: str) -> List` - Search files by path
- `get_stats() -> Dict` - Get detailed statistics

### ScheduledBaseIndexer

Extends `BaseIndexer` with background scheduling:

- `start()` - Start background indexing
- `stop()` - Stop background indexing

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Acknowledgments

Base Index is built with modern best practices for code intelligence platforms, incorporating research from leading academic sources and industry frameworks.

---

**Base Index v2.0** - Production-Grade Code Intelligence Platform

For detailed documentation, see [BASE_INDEX_DOCS.md](BASE_INDEX_DOCS.md)
