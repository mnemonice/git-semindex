import json

def _escape_xml(text):
    if not isinstance(text, str):
        return text
    return text.replace("<", "&lt;").replace(">", "&gt;")

def _escape_branch_data(branch):
    return {
        'branch_name': _escape_xml(branch.get('branch_name', '')),
        'latest_commits': [_escape_xml(c) for c in branch.get('latest_commits', [])],
        'files_changed': [_escape_xml(f) for f in branch.get('files_changed', [])]
    }

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
        Yields List of formatted strings, where each string represents
        a chunk of branches, ready to be dropped into an LLM prompt.
        Limits: Maximum 25 branches per chunk.
        Files Changed Truncation: Maximum 50 files per branch.
        """
        chunks = []
        current_chunk = []

        for branch in self.branches_metadata:
            # Escape XML-like tags to prevent Prompt Injection
            branch_copy = _escape_branch_data(branch)

            # Process files truncation
            files = branch_copy.get('files_changed', [])
            if len(files) > 50:
                truncated_files = files[:50]
                remaining = len(files) - 50
                truncated_files.append(f"...and {remaining} more files")
                branch_copy['files_changed'] = truncated_files

            current_chunk.append(branch_copy)

            if len(current_chunk) >= 25:
                chunks.append(self._format_chunk(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(self._format_chunk(current_chunk))

        return chunks

    def _format_chunk(self, chunk):
        # Separate metadata from file contents for the prompt
        git_metadata = []
        file_content_set = set()

        for branch in chunk:
            git_metadata.append({
                "branch_name": branch.get("branch_name", ""),
                "latest_commits": branch.get("latest_commits", [])
            })
            for f in branch.get("files_changed", []):
                file_content_set.add(f)

        file_content = list(file_content_set)
        # To make it deterministic for tests
        file_content.sort()

        return (
            "<source_context>\n"
            "  <git_metadata>\n"
            f"    {json.dumps(git_metadata)}\n"
            "  </git_metadata>\n"
            "  <file_content>\n"
            f"    {json.dumps(file_content)}\n"
            "  </file_content>\n"
            "</source_context>"
        )
