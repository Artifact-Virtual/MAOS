#!/usr/bin/env python3
"""
Test script to validate MAOS system functionality.
Tests each component independently and together.
"""
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

print("="*60)
print("MAOS System Test Suite")
print("="*60)

# Test 1: Import all modules
print("\n[Test 1] Testing module imports...")
try:
    from index_agent import IndexAgent
    print("✓ IndexAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import IndexAgent: {e}")
    sys.exit(1)

try:
    from rag_agent import RAGAgent
    print("✓ RAGAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import RAGAgent: {e}")
    sys.exit(1)

try:
    from reasoning_agent import ReasoningAgent
    print("✓ ReasoningAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import ReasoningAgent: {e}")
    sys.exit(1)

try:
    from code_agent import CodeAgent
    print("✓ CodeAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import CodeAgent: {e}")
    sys.exit(1)

try:
    from content_agent import ContentAgent
    print("✓ ContentAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import ContentAgent: {e}")
    sys.exit(1)

try:
    from vision_agent import VisionAgent
    print("✓ VisionAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import VisionAgent: {e}")
    sys.exit(1)

try:
    from orchestrator_agent import OrchestratorAgent
    print("✓ OrchestratorAgent imported successfully")
except Exception as e:
    print(f"✗ Failed to import OrchestratorAgent: {e}")
    sys.exit(1)

# Test 2: Create IndexAgent and test indexing
print("\n[Test 2] Testing IndexAgent...")
try:
    # Use Path(__file__).parent.parent to get workspace path relative to this test file
    workspace_path = Path(__file__).parent.parent.resolve()
    index_agent = IndexAgent(workspace_path, index_interval=300, initial_delay=0)
    print(f"✓ IndexAgent created for workspace: {workspace_path}")
    
    # Test immediate index update
    index_agent.update_index()
    file_count = len(index_agent.index.get('all_files', []))
    print(f"✓ Index updated successfully: {file_count} files indexed")
    
    if file_count == 0:
        print("⚠ Warning: No files were indexed")
    
except Exception as e:
    print(f"✗ IndexAgent test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Test RAGAgent
print("\n[Test 3] Testing RAGAgent...")
try:
    rag_agent = RAGAgent(index_agent)
    context = rag_agent.retrieve_context({"query": "test query"})
    print(f"✓ RAGAgent retrieved {len(context)} context files")
except Exception as e:
    print(f"✗ RAGAgent test failed: {e}")
    sys.exit(1)

# Test 4: Test agent processing (without Ollama they'll return mock responses)
print("\n[Test 4] Testing agent processing...")
try:
    reasoning_agent = ReasoningAgent(model="qwen3")
    result = reasoning_agent.process({"query": "test"}, context=[])
    print(f"✓ ReasoningAgent processed task: {result[:50]}...")
    
    code_agent = CodeAgent(model="codegeex4")
    result = code_agent.process({"query": "test"}, context=[])
    print(f"✓ CodeAgent processed task: {result[:50]}...")
    
    content_agent = ContentAgent(model="gemma3", workspace_root=str(workspace_path))
    result = content_agent.process({"query": "test"}, context=[])
    print(f"✓ ContentAgent processed task: {result[:50]}...")
    
    vision_agent = VisionAgent(model="llava")
    result = vision_agent.process({"query": "test"}, context=[])
    print(f"✓ VisionAgent processed task: {result[:50]}...")
    
except Exception as e:
    print(f"✗ Agent processing test failed: {e}")
    sys.exit(1)

# Test 5: Test content generation
print("\n[Test 5] Testing content generation...")
try:
    docs = content_agent.generate_docs(index_agent.index)
    doc_count = len(docs)
    total_chars = sum(len(content) for content in docs.values())
    print(f"✓ Generated {doc_count} documentation files")
    print(f"✓ Total documentation size: {total_chars} characters")
    
    charts = reasoning_agent.generate_charts(index_agent.index)
    chart_count = len(charts)
    print(f"✓ Generated {chart_count} charts")
    
except Exception as e:
    print(f"✗ Content generation test failed: {e}")
    sys.exit(1)

# Test 6: Test IndexAgent status
print("\n[Test 6] Testing IndexAgent status...")
try:
    status = index_agent.get_status()
    print(f"✓ IndexAgent status retrieved:")
    print(f"  - Last index time: {status['last_index_time']}")
    print(f"  - Indexed files: {status['indexed_files_count']}")
    print(f"  - Index interval: {status['index_interval']}s")
    print(f"  - Is running: {status['is_running']}")
except Exception as e:
    print(f"✗ Status test failed: {e}")
    sys.exit(1)

# Test 7: Test utils module
print("\n[Test 7] Testing utils module...")
try:
    from utils.create_index import scan_directory
    files = scan_directory(workspace_path, ignore_patterns=['__pycache__', '.git'])
    print(f"✓ scan_directory found {len(files)} files")
except Exception as e:
    print(f"✗ Utils module test failed: {e}")
    sys.exit(1)

# Final summary
print("\n" + "="*60)
print("All tests passed! ✓")
print("="*60)
print("\nSystem Status:")
print(f"  • IndexAgent: Working ({file_count} files indexed)")
print(f"  • RAGAgent: Working")
print(f"  • ReasoningAgent: Working (mock mode without Ollama)")
print(f"  • CodeAgent: Working (mock mode without Ollama)")
print(f"  • ContentAgent: Working")
print(f"  • VisionAgent: Working (mock mode without Ollama)")
print(f"  • Utils: Working")
print("\nNote: For full AI functionality, install Ollama from https://ollama.ai/")
print("      and pull the required models: qwen3, codegeex4, gemma3, llava")
