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

/// Placeholder function to list local branches and return their metadata.
/// Extracts structural intent rather than focusing on textual diffs.
#[pyfunction]
fn list_local_branches() -> PyResult<Vec<BranchMetadata>> {
    let mut branches_metadata = Vec::new();

    // Attempt to open the repository in the current directory.
    let repo = match Repository::open(".") {
        Ok(repo) => repo,
        Err(_) => {
            // Return an empty list if not a git repository or other error.
            return Ok(branches_metadata);
        }
    };

    // Iterate over local branches.
    let branches = match repo.branches(Some(BranchType::Local)) {
        Ok(branches) => branches,
        Err(_) => return Ok(branches_metadata),
    };

    for branch_result in branches {
        if let Ok((branch, _)) = branch_result {
            if let Ok(Some(name)) = branch.name() {
                // For scaffolding purposes, we are just returning the branch name
                // and placeholder data for commits and files_changed.
                // In the future, this will use git2 to extract real semantic metadata.
                let metadata = BranchMetadata {
                    branch_name: name.to_string(),
                    latest_commits: vec!["Placeholder commit 1".to_string()],
                    files_changed: vec!["Placeholder file 1".to_string()],
                };
                branches_metadata.push(metadata);
            }
        }
    }

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
            latest_commits: vec!["Initial commit".to_string()],
            files_changed: vec!["README.md".to_string()],
        };
        assert_eq!(metadata.branch_name, "main");
        assert_eq!(metadata.latest_commits.len(), 1);
        assert_eq!(metadata.files_changed.len(), 1);
    }
}
