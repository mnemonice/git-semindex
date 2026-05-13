import pytest
import subprocess
from git_semindex import list_local_branches, _shell_list_local_branches

def test_shell_fallback():
    """Test that the shell fallback returns a list of dictionaries with correct keys."""
    # Ensure git is initialized for the test to work
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except Exception:
        pytest.skip("Not a git repository or git not installed")

    branches = _shell_list_local_branches()
    assert isinstance(branches, list)

    # If the repository has branches, test the structure
    if len(branches) > 0:
        branch = branches[0]
        assert isinstance(branch, dict)
        assert 'branch_name' in branch
        assert 'latest_commits' in branch
        assert 'files_changed' in branch
        assert isinstance(branch['latest_commits'], list)
        assert isinstance(branch['files_changed'], list)

def test_list_local_branches():
    """Test the main entry point."""
    try:
        subprocess.run(['git', 'status'], capture_output=True, check=True)
    except Exception:
        pytest.skip("Not a git repository or git not installed")

    branches = list_local_branches()
    assert isinstance(branches, list)
