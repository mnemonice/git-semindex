use pyo3::prelude::*;
use pyo3::types::PyDict;
use git2::{Repository, BranchType};

/// Represents metadata extracted from a git branch.
/// Adheres to the "Semantic Extraction over Textual Merging" paradigm.
#[pyclass]
#[derive(Clone, Debug)]
pub struct BranchMetadata {
    #[pyo3(get)]
    pub branch_name: String,
    #[pyo3(get)]
    pub latest_commits: Vec<String>,
    #[pyo3(get)]
    pub files_changed: Vec<String>,
}

#[pymethods]
impl BranchMetadata {
    /// Converts the struct to a Python dictionary.
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<&'py PyDict> {
        let dict = PyDict::new(py);
        dict.set_item("branch_name", &self.branch_name)?;
        dict.set_item("latest_commits", &self.latest_commits)?;
        dict.set_item("files_changed", &self.files_changed)?;
        Ok(dict)
    }
}

/// Helper function to fetch branch metadata using git2.
fn extract_metadata(repo: &Repository) -> Result<Vec<BranchMetadata>, git2::Error> {
    let mut branches_metadata = Vec::new();

    // Find default branch
    let default_branch = repo.find_branch("main", BranchType::Local)
        .or_else(|_| repo.find_branch("master", BranchType::Local))
        .ok();

    let default_commit = default_branch.as_ref().and_then(|b| b.get().peel_to_commit().ok());
    let default_branch_name = default_branch.as_ref().and_then(|b| b.name().ok().flatten());

    let branches = repo.branches(Some(BranchType::Local))?;

    for branch_result in branches {
        if let Ok((branch, _)) = branch_result {
            if let Ok(Some(name)) = branch.name() {
                let mut latest_commits = Vec::new();
                let mut files_changed = Vec::new();

                let is_default = default_branch_name == Some(name);

                if let Ok(commit) = branch.get().peel_to_commit() {
                    // Get latest 3 commits
                    if let Ok(mut revwalk) = repo.revwalk() {
                        if revwalk.push(commit.id()).is_ok() {
                            for (i, id_result) in revwalk.enumerate() {
                                if i >= 3 { break; }
                                if let Ok(id) = id_result {
                                    if let Ok(c) = repo.find_commit(id) {
                                        let short_id = c.id().to_string().chars().take(7).collect::<String>();
                                        let summary = c.summary().unwrap_or("").to_string();
                                        latest_commits.push(format!("{} {}", short_id, summary));
                                    }
                                }
                            }
                        }
                    }

                    // Get diff if not default branch
                    if !is_default {
                        if let Some(default_c) = &default_commit {
                            if let Ok(base_oid) = repo.merge_base(commit.id(), default_c.id()) {
                                if let Ok(base_commit) = repo.find_commit(base_oid) {
                                    if let Ok(base_tree) = base_commit.tree() {
                                        if let Ok(branch_tree) = commit.tree() {
                                            if let Ok(diff) = repo.diff_tree_to_tree(Some(&base_tree), Some(&branch_tree), None) {
                                                for delta in diff.deltas() {
                                                    if let Some(path) = delta.new_file().path() {
                                                        files_changed.push(path.to_string_lossy().into_owned());
                                                    }
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }

                let metadata = BranchMetadata {
                    branch_name: name.to_string(),
                    latest_commits,
                    files_changed,
                };
                branches_metadata.push(metadata);
            }
        }
    }

    Ok(branches_metadata)
}

/// Extracts structural intent rather than focusing on textual diffs.
#[pyfunction]
fn list_local_branches() -> PyResult<Vec<BranchMetadata>> {
    // Attempt to open the repository in the current directory.
    let repo = match Repository::open(".") {
        Ok(repo) => repo,
        Err(_) => return Ok(Vec::new()),
    };

    let branches_metadata = extract_metadata(&repo).unwrap_or_else(|_| Vec::new());
    Ok(branches_metadata)
}

/// The git_semindex Python module implemented in Rust.
#[pymodule]
fn _git_semindex(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_class::<BranchMetadata>()?;
    m.add_function(wrap_pyfunction!(list_local_branches, m)?)?;
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_branch_metadata_creation() {
        let metadata = BranchMetadata {
            branch_name: "main".to_string(),
            latest_commits: vec!["a1b2c3d Initial commit".to_string()],
            files_changed: vec!["README.md".to_string()],
        };
        assert_eq!(metadata.branch_name, "main");
        assert_eq!(metadata.latest_commits.len(), 1);
        assert_eq!(metadata.files_changed.len(), 1);
    }
}
