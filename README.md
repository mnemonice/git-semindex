# git-semindex

`git-semindex` is a high-performance Rust/Python library for semantic Git archaeology. It uses a Map-Reduce protocol to index massive branch histories without blowing AI context windows. Designed for agentic workflows, it enables "lost code" recovery and PR consolidation through semantic intent extraction rather than mechanical merging.

## Philosophy: Semantic Extraction over Textual Merging

Traditional git merging focuses on resolving textual conflicts line-by-line. This mechanical approach often loses the broader intent behind changes, leading to fragile merges or completely lost context when branches diverge too far.

`git-semindex` embraces a different paradigm: **Semantic Extraction over Textual Merging**. Instead of blindly attempting to smash code together, it leverages a Map-Reduce protocol across branch histories to index metadata, abstracting away the noise to surface the *semantic intent* of code changes. This empowers agentic workflows to intelligently reason about diverging branches and recover "lost" code seamlessly.

## Hybrid Execution Architecture

To guarantee robustness across different environments (including constrained systems like Termux on Android), `git-semindex` employs a **Two-Tier Execution Architecture**:

1. **Tier 1: High-Performance Native Rust Core**: The primary execution path. A highly-optimized PyO3 C-extension (`git_semindex._git_semindex`) utilizing the `git2` crate for native, blistering-fast git operations.
2. **Tier 2: Universal Shell Fallback**: In environments where native C-extensions are unavailable (e.g., missing pre-compiled wheels for an exotic architecture), the library falls back directly to invoking the standard system `git` binary via subprocess. While slower, this guarantees the library remains completely functional everywhere `git` and Python exist.
