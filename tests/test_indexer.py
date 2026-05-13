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

    chunk1 = json.loads(chunks[0])
    assert len(chunk1) == 25

    chunk3 = json.loads(chunks[2])
    assert len(chunk3) == 10

    # Test truncation
    branch0_files = chunk1[0]['files_changed']
    assert len(branch0_files) == 51 # 50 files + 1 string
    assert branch0_files[-1] == "...and 10 more files"
