import json
from git_semindex.indexer import SemanticIndexer

def test_indexer_chunking():
    indexer = SemanticIndexer()

    # Add 60 branches
    branches = []
    for i in range(60):
        branches.append({
            'branch_name': f'branch-{i}',
            'latest_commits': ['commit1'],
            'files_changed': [f'file-{j}.txt' for j in range(60)] # 60 files to trigger truncation
        })

    indexer.add_branches(branches)

    chunks = indexer.chunk_metadata()

    # 60 branches / 25 = 3 chunks (25, 25, 10)
    assert len(chunks) == 3


    # Parse XML-like structure
    import re
    match1 = re.search(r'<git_metadata>\s*(.*?)\s*</git_metadata>', chunks[0], re.DOTALL)
    chunk1 = json.loads(match1.group(1))
    match_files = re.search(r'<file_content>\s*(.*?)\s*</file_content>', chunks[0], re.DOTALL)
    chunk1_files = json.loads(match_files.group(1))

    assert len(chunk1) == 25


    match3 = re.search(r'<git_metadata>\s*(.*?)\s*</git_metadata>', chunks[2], re.DOTALL)
    chunk3 = json.loads(match3.group(1))

    assert len(chunk3) == 10

    # Test truncation
    branch0_files = chunk1_files
    assert len(branch0_files) == 51 # 50 files + 1 string
    assert "...and 10 more files" in branch0_files

def test_prompt_injection_escaping():
    indexer = SemanticIndexer()

    indexer.add_branches([{
        'branch_name': 'hack<script>alert(1)</script>',
        'latest_commits': ['feat: add <hack> tag'],
        'files_changed': ['src/<bad>.rs']
    }])

    chunks = indexer.chunk_metadata()
    assert len(chunks) == 1

    output = chunks[0]

    assert '<script>' not in output
    assert '&lt;script&gt;' in output
    assert '<hack>' not in output
    assert '&lt;hack&gt;' in output
    assert '<bad>' not in output
    assert '&lt;bad&gt;' in output

    assert output.startswith("<source_context>")
    assert output.endswith("</source_context>")
    assert "<git_metadata>" in output
    assert "<file_content>" in output
