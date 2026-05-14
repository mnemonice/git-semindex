import subprocess
import logging

logger = logging.getLogger(__name__)

# Try to load the native Rust extension (Tier 1)
try:
    from ._git_semindex import list_local_branches as _rust_list_local_branches

    def list_local_branches():
        """
        List local branches and their semantic metadata.
        Uses the high-performance native Rust core.
        """
        try:
            return [
                {
                    "branch_name": b.branch_name,
                    "latest_commits": b.latest_commits,
                    "files_changed": b.files_changed
                }
                for b in _rust_list_local_branches()
            ]
        except Exception as e:
            logger.warning(f"Rust extension failed to execute: {e}. Falling back to shell.")
            return _shell_list_local_branches()

except ImportError:
    # Fallback to subprocess shell calls (Tier 2)
    logger.info("Native Rust extension not found. Falling back to universal shell implementation.")

    def list_local_branches():
        """
        List local branches and their semantic metadata.
        Uses the universal shell fallback.
        """
        return _shell_list_local_branches()

def _shell_list_local_branches():
    """
    Tier 2: Universal Shell Fallback implementation.
    Calls system `git` to extract basic structural intent.
    """
    try:
        # Get list of local branches
        result = subprocess.run(
            ['git', 'branch', '--format=%(refname:short)'],
            capture_output=True, text=True, check=True
        )
        branch_names = [b.strip() for b in result.stdout.split('\n') if b.strip()]

        # Find default branch
        default_branch = None
        if 'main' in branch_names:
            default_branch = 'main'
        elif 'master' in branch_names:
            default_branch = 'master'

        metadata_list = []
        for branch in branch_names:
            # Get latest 3 commits
            try:
                commits_result = subprocess.run(
                    ['git', 'log', '-n', '3', '--format=%h %s', '--', branch],
                    capture_output=True, text=True, check=True
                )
                latest_commits = [c.strip() for c in commits_result.stdout.split('\n') if c.strip()]
            except subprocess.CalledProcessError:
                latest_commits = []

            # Get files changed
            files_changed = []
            if default_branch and branch != default_branch:
                try:
                    diff_result = subprocess.run(
                        ['git', 'diff', '--name-only', '--', f'{default_branch}...{branch}'],
                        capture_output=True, text=True, check=True
                    )
                    files_changed = [f.strip() for f in diff_result.stdout.split('\n') if f.strip()]
                except subprocess.CalledProcessError:
                    # Ignore errors, e.g. when there's no common ancestry or branch doesn't exist anymore
                    pass

            metadata = {
                'branch_name': branch,
                'latest_commits': latest_commits,
                'files_changed': files_changed
            }
            metadata_list.append(metadata)

        return metadata_list
    except subprocess.CalledProcessError as e:
        logger.error(f"Git shell command failed: {e}")
        return []
    except FileNotFoundError:
        logger.error("Git executable not found in PATH.")
        return []

from .indexer import SemanticIndexer
__all__ = ["list_local_branches", "SemanticIndexer"]
