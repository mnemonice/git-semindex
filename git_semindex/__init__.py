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
            return _rust_list_local_branches()
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
        branch_names = [b.strip() for b in result.stdout.splitlines() if b.strip()]

        metadata_list = []
        for branch in branch_names:
            # Note: This is a scaffold. In a full implementation, we would extract
            # real 'latest_commits' and 'files_changed' via further git shell commands.
            metadata = {
                'branch_name': branch,
                'latest_commits': ["Placeholder shell commit 1"],
                'files_changed': ["Placeholder shell file 1"]
            }
            metadata_list.append(metadata)

        return metadata_list
    except subprocess.CalledProcessError as e:
        logger.error(f"Git shell command failed: {e}")
        return []
    except FileNotFoundError:
        logger.error("Git executable not found in PATH.")
        return []
