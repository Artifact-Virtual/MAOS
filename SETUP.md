# MAOS Setup and Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Git (for cloning the repository)

## Quick Start

### 1. Install Python Dependencies

```bash
# From the MAOS directory
pip install -r requirements.txt
```

### 2. Test the System

```bash
# Run the comprehensive test suite
python3 test_system.py
```

You should see all tests pass with output showing:
- ✓ All modules imported successfully
- ✓ IndexAgent working
- ✓ All agents functional
- ✓ File indexing operational

### 3. Run the Orchestrator

```bash
# Run the main orchestrator
python3 orchestrator_agent.py
```

The system will:
1. Start up (with warnings about Ollama if not installed)
2. Begin indexing your workspace
3. Run agent tasks
4. Generate documentation in `../docs/README_AUTO.md`
5. Generate charts in `../charts/`
6. Enter maintenance mode (press Ctrl+C to exit gracefully)

## Optional: Install Ollama for AI Features

MAOS is designed to work with Ollama for advanced AI capabilities. Without Ollama, the system runs in "mock mode" with simulated responses.

### Install Ollama

1. Visit https://ollama.ai/
2. Download and install Ollama for your platform
3. Pull the required models:

```bash
ollama pull qwen3
ollama pull codegeex4
ollama pull gemma3
ollama pull llava
```

### Verify Ollama Installation

```bash
ollama list
```

You should see the four models listed.

## System Architecture

```
MAOS/
├── orchestrator_agent.py      # Main orchestration system
├── index_agent.py             # File indexing with scheduled updates
├── rag_agent.py               # Context retrieval system
├── reasoning_agent.py         # Reasoning capabilities (Qwen3)
├── code_agent.py              # Code generation (CodeGeeX4)
├── content_agent.py           # Documentation generation (Gemma3)
├── vision_agent.py            # Image processing (Llava)
├── orchestration_watcher.py   # File system watcher
├── utils/
│   ├── __init__.py
│   └── create_index.py        # Indexing utilities
├── test_system.py             # Comprehensive test suite
└── requirements.txt           # Python dependencies
```

## Configuration

### Index Interval

The orchestrator indexes files at regular intervals. Default is 60 seconds. To change:

```python
orchestrator = OrchestratorAgent(
    workspace_root="..",
    index_interval=300,  # 5 minutes
    initial_delay=10     # 10 seconds before first index
)
```

### Workspace Root

By default, the system indexes the parent directory (`..`). To change:

```python
orchestrator = OrchestratorAgent(
    workspace_root="/path/to/your/workspace",
    index_interval=60,
    initial_delay=5
)
```

## Usage Examples

### Example 1: Quick Test

```bash
python3 test_system.py
```

### Example 2: Run Orchestrator

```bash
python3 orchestrator_agent.py
```

### Example 3: Use Individual Agents

```python
from index_agent import IndexAgent
from rag_agent import RAGAgent
from content_agent import ContentAgent

# Create and run index
index_agent = IndexAgent(".", index_interval=60)
index_agent.update_index()

# Retrieve context
rag_agent = RAGAgent(index_agent)
context = rag_agent.retrieve_context({"query": "python scripts"})

# Generate documentation
content_agent = ContentAgent(workspace_root=".")
docs = content_agent.generate_docs(index_agent.index)
```

### Example 4: File System Watcher

```bash
python3 orchestration_watcher.py
```

This watches for file changes and automatically triggers the orchestrator.

## Troubleshooting

### Issue: "Could not find workspace root"
**Solution**: This has been fixed. The system now uses the current directory as fallback if `requirements.txt` is not found in parent directories.

### Issue: "No such file or directory: 'ollama'"
**Solution**: This is a warning, not an error. The system works without Ollama in mock mode. To enable full AI features, install Ollama as described above.

### Issue: "ImportError: No module named 'watchdog'"
**Solution**: Install dependencies:
```bash
pip install -r requirements.txt
```

### Issue: No files indexed
**Solution**: Check that you're running from the correct directory and that files exist in the workspace.

### Issue: Permission errors during cleanup
**Solution**: This is normal for temporary files that may already be deleted. The system handles these gracefully.

## Generated Files

The system creates the following files:

- `../docs/README_AUTO.md` - Auto-generated workspace documentation
- `../charts/workspace_overview.png` - Workspace visualization chart
- Various temporary files that are cleaned up automatically

## System Requirements

- **Memory**: Minimum 2GB RAM (4GB+ recommended with Ollama)
- **Disk**: 100MB for code + space for indexed files
- **CPU**: Any modern processor (multi-core recommended with Ollama)
- **OS**: Linux, macOS, or Windows

## Features

✓ **Automated File Indexing** - Scans and indexes workspace files every 60 seconds  
✓ **Scheduled Updates** - Cron-like scheduling with configurable intervals  
✓ **Context Retrieval** - RAG-based context system for relevant file retrieval  
✓ **Multi-Agent System** - Specialized agents for different tasks  
✓ **Graceful Cleanup** - Automatic cleanup of temporary files on exit  
✓ **Error Handling** - Comprehensive error recovery and logging  
✓ **Mock Mode** - Works without external dependencies  
✓ **Real AI Mode** - Enhanced capabilities with Ollama  

## Next Steps

1. Run `python3 test_system.py` to verify installation
2. Run `python3 orchestrator_agent.py` to start the system
3. (Optional) Install Ollama for AI features
4. Check `../docs/README_AUTO.md` for generated documentation
5. Review logs for system activity

## Support

For issues or questions:
1. Check this guide first
2. Review the generated logs
3. Run the test suite: `python3 test_system.py`
4. Check that all dependencies are installed

## License

MIT License - See LICENSE file for details
