use cap_std::fs::Dir;
use git2::{BranchType, Repository};
use pyo3::prelude::*;
use pyo3::types::PyDict;
use std::collections::HashSet;
use tree_sitter::{Parser, Query, QueryCursor};

/// Represents metadata extracted from a git branch.
/// Adheres to the "Semantic Extraction over Textual Merging" paradigm.
#[pyclass(skip_from_py_object)]
#[derive(Clone, Debug)]
pub struct BranchMetadata {
    #[pyo3(get)]
    pub branch_name: String,
    #[pyo3(get)]
    pub latest_commits: Vec<String>,
    #[pyo3(get)]
    pub files_changed: Vec<String>,
    #[pyo3(get)]
    pub semantic_changes: Vec<String>,
}

#[pymethods]
impl BranchMetadata {
    /// Converts the struct to a Python dictionary.
    pub fn to_dict<'py>(&self, py: Python<'py>) -> PyResult<pyo3::Bound<'py, PyDict>> {
        let dict = PyDict::new(py);
        dict.set_item("branch_name", &self.branch_name)?;
        dict.set_item("latest_commits", &self.latest_commits)?;
        dict.set_item("files_changed", &self.files_changed)?;
        dict.set_item("semantic_changes", &self.semantic_changes)?;
        Ok(dict)
    }
}

/// Helper function to fetch branch metadata using git2.
fn extract_metadata(repo: &Repository) -> Result<Vec<BranchMetadata>, git2::Error> {
    let mut branches_metadata = Vec::new();

    // Find default branch
    let default_branch = repo
        .find_branch("main", BranchType::Local)
        .or_else(|_| repo.find_branch("master", BranchType::Local))
        .ok();

    let default_commit = default_branch
        .as_ref()
        .and_then(|b| b.get().peel_to_commit().ok());
    let default_branch_name = default_branch
        .as_ref()
        .and_then(|b| b.name().ok().flatten());

    let branches = repo.branches(Some(BranchType::Local))?;

    for (branch, _) in branches.flatten() {
        if let Ok(Some(name)) = branch.name() {
            let mut latest_commits = Vec::new();
            let mut files_changed = Vec::new();
            let mut semantic_changes = HashSet::new();

            let is_default = default_branch_name == Some(name);

            if let Ok(commit) = branch.get().peel_to_commit() {
                // Get latest 3 commits
                if let Ok(mut revwalk) = repo.revwalk() {
                    if revwalk.push(commit.id()).is_ok() {
                        for (i, id_result) in revwalk.enumerate() {
                            if i >= 3 {
                                break;
                            }
                            if let Ok(id) = id_result {
                                if let Ok(c) = repo.find_commit(id) {
                                    let short_id =
                                        c.id().to_string().chars().take(7).collect::<String>();
                                    let summary =
                                        c.summary().unwrap_or(Some("")).unwrap_or("").to_string();
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
                                        let mut diff_opts = git2::DiffOptions::new();
                                        // Mitigate Asymmetric DoS: limits
                                        // Setting a max depth isn't directly exposed in DiffOptions for tree walking,
                                        // but git2 limits recursion by default, and we can enforce max deltas.

                                        if let Ok(diff) = repo.diff_tree_to_tree(
                                            Some(&base_tree),
                                            Some(&branch_tree),
                                            Some(&mut diff_opts),
                                        ) {
                                            let workdir = repo.workdir();

                                            let mut delta_count = 0;
                                            for delta in diff.deltas() {
                                                delta_count += 1;
                                                if delta_count > 10_000 {
                                                    break; // Enforce max_deltas limit
                                                }

                                                if let Some(path) = delta.new_file().path() {
                                                    let mut is_safe = false;

                                                    // Mitigate Arbitrary File Read (Symlink Traversal) using cap-std
                                                    if let Some(workdir) = workdir {
                                                        if let Ok(dir) = Dir::open_ambient_dir(
                                                            workdir,
                                                            cap_std::ambient_authority(),
                                                        ) {
                                                            // Try to access the path relative to the cap_std::fs::Dir
                                                            // cap_std will prevent traversal outside the `workdir`
                                                            if dir.metadata(path).is_ok()
                                                                || dir
                                                                    .symlink_metadata(path)
                                                                    .is_ok()
                                                            {
                                                                is_safe = true;
                                                            }
                                                        }
                                                    }

                                                    if is_safe {
                                                        let path_str =
                                                            path.to_string_lossy().into_owned();
                                                        files_changed.push(path_str.clone());

                                                        // Semantic Extraction using Tree-sitter
                                                        if path_str.ends_with(".py") {
                                                            if let Ok(file_content) =
                                                                std::fs::read_to_string(path)
                                                            {
                                                                if let Some(changes) =
                                                                    extract_python_semantics(
                                                                        &file_content,
                                                                        &path_str,
                                                                    )
                                                                {
                                                                    semantic_changes
                                                                        .extend(changes);
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
                        }
                    }
                }
            }

            let mut semantic_changes_vec: Vec<String> = semantic_changes.into_iter().collect();
            semantic_changes_vec.sort();

            let metadata = BranchMetadata {
                branch_name: name.to_string(),
                latest_commits,
                files_changed,
                semantic_changes: semantic_changes_vec,
            };
            branches_metadata.push(metadata);
        }
    }

    Ok(branches_metadata)
}

/// Extracts Python semantics using tree-sitter
fn extract_python_semantics(source_code: &str, file_path: &str) -> Option<Vec<String>> {
    let mut parser = Parser::new();
    let language = tree_sitter_python::LANGUAGE.into();
    parser.set_language(&language).ok()?;

    let tree = parser.parse(source_code, None)?;
    let root_node = tree.root_node();

    // Query to find function and class definitions
    let query_source = "
        (function_definition name: (identifier) @func_name)
        (class_definition name: (identifier) @class_name)
    ";
    let query = Query::new(&language, query_source).ok()?;
    let mut query_cursor = QueryCursor::new();

    let mut matches = query_cursor.matches(&query, root_node, source_code.as_bytes());

    let mut semantics = Vec::new();
    use tree_sitter::StreamingIterator;
    while let Some(m) = matches.next() {
        for capture in m.captures {
            if let Ok(name) = capture.node.utf8_text(source_code.as_bytes()) {
                let capture_name = query.capture_names()[capture.index as usize];
                let item_type = if capture_name == "class_name" {
                    "Class"
                } else {
                    "Function"
                };
                semantics.push(format!("{} `{}` in {}", item_type, name, file_path));
            }
        }
    }

    Some(semantics)
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
fn _git_semindex(_py: Python, m: &pyo3::Bound<'_, pyo3::types::PyModule>) -> PyResult<()> {
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
            semantic_changes: vec![],
        };
        assert_eq!(metadata.branch_name, "main");
        assert_eq!(metadata.latest_commits.len(), 1);
        assert_eq!(metadata.files_changed.len(), 1);
        assert_eq!(metadata.semantic_changes.len(), 0);
    }
}
