import pytest
import subprocess
from git_semindex import list_local_branches, _shell_list_local_branches

import os
import pathlib
import tempfile
from unittest.mock import patch, MagicMock

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

def test_shell_fallback_security_boundary():
    """Test that the shell fallback filters out paths traversing outside the repository."""
    # Use two temporary directories to avoid polluting the system /tmp
    with tempfile.TemporaryDirectory() as base_dir:
        base_path = pathlib.Path(base_dir).resolve()

        # This will act as our fake "outside" filesystem
        outside_file = base_path / "outside_file.txt"
        outside_file.touch()

        # This will act as our fake repository root
        repo_path = base_path / "fake_repo"
        repo_path.mkdir()

        # Create a safe file inside the repo
        safe_file = repo_path / "safe_file.txt"
        safe_file.touch()

        # Create a malicious symlink inside pointing outside
        malicious_symlink = repo_path / "malicious.txt"
        try:
            os.symlink(outside_file, malicious_symlink)
        except OSError:
            # Skip symlink test if we don't have permission (e.g. Windows)
            pass

        with patch('subprocess.run') as mock_run:
            # Mock git branch output
            mock_branch_result = MagicMock()
            mock_branch_result.stdout = "main\nfeature"

            # Mock git log output
            mock_log_result = MagicMock()
            mock_log_result.stdout = "abc1234 Initial commit"

            # Mock git diff output - simulate a malicious symlink or traversal
            mock_diff_result = MagicMock()
            mock_diff_result.stdout = "safe_file.txt\n../outside_file.txt\n/etc/passwd\nmalicious.txt"

            # Mock git rev-parse output to be our temp directory
            mock_rev_parse_result = MagicMock()
            mock_rev_parse_result.stdout = str(repo_path)

            def side_effect(*args, **kwargs):
                cmd = args[0]
                if cmd[1] == 'branch':
                    return mock_branch_result
                elif cmd[1] == 'log':
                    return mock_log_result
                elif cmd[1] == 'diff':
                    return mock_diff_result
                elif cmd[1] == 'rev-parse':
                    return mock_rev_parse_result
                raise subprocess.CalledProcessError(1, cmd)

            mock_run.side_effect = side_effect

            # Monkey patch pathlib.Path to use our temp dir as base for the test
            # Because _shell_list_local_branches uses pathlib.Path(".").resolve() as fallback
            # and (repo_root / f).resolve() for resolution
            # We don't really need to monkey patch if we mock rev-parse and cd into the dir
            old_cwd = os.getcwd()
            try:
                os.chdir(str(repo_path))
                branches = _shell_list_local_branches()
            finally:
                os.chdir(old_cwd)

            feature_branch = next((b for b in branches if b['branch_name'] == 'feature'), None)
            assert feature_branch is not None

            # The safe file should be included
            assert 'safe_file.txt' in feature_branch['files_changed']

            # The malicious files (../outside_file.txt, /etc/passwd) should be filtered out
            # pathlib.Path('/etc/passwd').resolve() won't have repo_root in parents
            assert '../outside_file.txt' not in feature_branch['files_changed']
            assert '/etc/passwd' not in feature_branch['files_changed']

            # The malicious symlink should be filtered out if it was created
            if malicious_symlink.exists():
                assert 'malicious.txt' not in feature_branch['files_changed']
