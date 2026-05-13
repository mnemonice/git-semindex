import json

class SemanticIndexer:
    """
    Map-Reduce Orchestrator for Git Semantic Extraction.
    Takes a massive list of branch metadata, chunks it safely,
    and formats it for LLMs to consume without blowing the context window.
    """

    def __init__(self, branches_metadata=None):
        self.branches_metadata = branches_metadata or []

    def add_branches(self, branches):
        """Add branch metadata dictionaries."""
        self.branches_metadata.extend(branches)

    def chunk_metadata(self):
        """
        Yields List of JSON-formatted strings, where each string represents
        a chunk of branches, ready to be dropped into an LLM prompt.
        Limits: Maximum 25 branches per chunk.
        Files Changed Truncation: Maximum 50 files per branch.
        """
        chunks = []
        current_chunk = []

        for branch in self.branches_metadata:
            # Create a copy so we don't mutate input data reference
            branch_copy = branch.copy()

            # Process files truncation
            files = branch_copy.get('files_changed', [])
            if len(files) > 50:
                truncated_files = files[:50]
                remaining = len(files) - 50
                truncated_files.append(f"...and {remaining} more files")
                branch_copy['files_changed'] = truncated_files

            current_chunk.append(branch_copy)

            if len(current_chunk) >= 25:
                chunks.append(json.dumps(current_chunk, indent=2))
                current_chunk = []

        if current_chunk:
            chunks.append(json.dumps(current_chunk, indent=2))

        return chunks
