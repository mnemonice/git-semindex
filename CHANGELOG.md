# Changelog

## 0.1.0 (2026-05-15)


### Features

* implement dedicated ci pipeline, security policy, and cap-std architectural enhancements ([21b12f3](https://github.com/MnemOnicE/git-semindex/commit/21b12f33653bef32ca09192497756e63a7babe79))
* implement dedicated ci pipeline, security policy, and cap-std architectural enhancements ([0003d52](https://github.com/MnemOnicE/git-semindex/commit/0003d5256b4fcc36bbd389c19a2055eeb88308a3))
* Initial git-semindex Scaffold with Tiered Architecture ([2a025fb](https://github.com/MnemOnicE/git-semindex/commit/2a025fbd6a33cbcaa5b7d99caab5290f294fe54f))
* Scaffold Map-Reduce structure and Tiered Execution Architecture ([2f3e5fd](https://github.com/MnemOnicE/git-semindex/commit/2f3e5fd7cf6b9b8c39e1f28d4d2db2b9f11bd50a))


### Bug Fixes

* address security vulnerabilities in semantic indexer ([ebab949](https://github.com/MnemOnicE/git-semindex/commit/ebab949782d1e8ed11811c57536f9374865f0c4f))
* apply CodeRabbit auto-fixes ([d1e0140](https://github.com/MnemOnicE/git-semindex/commit/d1e0140132353d13b6efde4042b343b7239b1574))
* disable git2 default features avoiding openssl-sys cross-platform constraints, use-cross action matrix resolution ([1f2ede1](https://github.com/MnemOnicE/git-semindex/commit/1f2ede19c5d1d949c3863167e30f8ccd0720d1a9))
* implement capability-based security boundary in python fallback ([2e0cf4f](https://github.com/MnemOnicE/git-semindex/commit/2e0cf4fb1251d578aa3c56287655d1b639d87ccc))
* implement capability-based security boundary in python fallback\n\nThe Tier 2 Python shell fallback lacked a capability-based security boundary, allowing potential arbitrary file read vulnerabilities if malicious symlinks or directory traversal sequences were introduced in the git diff output.\n\nThis change uses pathlib to resolve file paths extracted from git diff and verifies they reside within the calculated repository root, mitigating the vulnerability entirely using the Python standard library. ([65f4729](https://github.com/MnemOnicE/git-semindex/commit/65f4729ab0974458853976fb1ac2f41c05e40bb4))
* resolve CI failures by fixing pyo3 issues and removing cargo-audit ([5848921](https://github.com/MnemOnicE/git-semindex/commit/584892139d10fde3c75d24e888fce4d50949954b))
* resolve CI failures by fixing pyo3 issues and removing cargo-audit ([830c488](https://github.com/MnemOnicE/git-semindex/commit/830c488633f820a4c4f6d718a96ea1b44d78276c))
* resolve clippy deprecated attribute error for pyclass ([2ffc57b](https://github.com/MnemOnicE/git-semindex/commit/2ffc57bf35ec106317eafc48b094c29f8e20974a))
* resolve critical security and performance bottlenecks ([cf66159](https://github.com/MnemOnicE/git-semindex/commit/cf6615913df57cd946164128e63dc817a0ded644))
* resolve critical security and performance bottlenecks ([fe61d35](https://github.com/MnemOnicE/git-semindex/commit/fe61d35eede14010da32b09298ef87e2526d079e))
* secure python fallback boundary\n\nThe Tier 2 Python shell fallback lacked a capability-based security boundary,\nallowing potential arbitrary file read vulnerabilities if malicious symlinks or\ndirectory traversal sequences were introduced in the git diff output.\n\nThis change uses pathlib to resolve file paths extracted from git diff and\nverifies they reside within the calculated repository root, mitigating the\nvulnerability entirely using the Python standard library. ([e534008](https://github.com/MnemOnicE/git-semindex/commit/e534008d5213844c543ae89667e5abf87ea3b23c))
* secure python fallback boundary\n\nThe Tier 2 Python shell fallback lacked a capability-based security boundary,\nallowing potential arbitrary file read vulnerabilities if malicious symlinks or\ndirectory traversal sequences were introduced in the git diff output.\n\nThis change uses pathlib to resolve file paths extracted from git diff and\nverifies they reside within the calculated repository root, mitigating the\nvulnerability entirely using the Python standard library. ([d745b5d](https://github.com/MnemOnicE/git-semindex/commit/d745b5d2dfcb82fe0dd7e6bdec88ac48992258a7))
* Security and performance audit fixes ([71d6fbc](https://github.com/MnemOnicE/git-semindex/commit/71d6fbccf3f40acb824e087344b3efaad7e8a2f6))
