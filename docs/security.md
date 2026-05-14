# Security Policy

## Supported Versions

Currently, only the latest `main` branch and the latest published version are supported with security updates.

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x   | :white_check_mark: |
| < 0.1.0 | :x:                |

## Reporting a Vulnerability

Security is a primary concern for `git-semindex`, especially given its target use case in agentic workflows where arbitrary repositories might be analyzed.

If you discover a security vulnerability (such as a bypass of the symlink traversal mitigations, arbitrary file read, or potential denial of service via memory exhaustion), please do **NOT** open a public issue.

Instead, please report the vulnerability using GitHub's **Private Vulnerability Reporting**:
1. Go to the repository's "Security" tab.
2. Click on "Report a vulnerability" to open a private advisory.

If private vulnerability reporting is not enabled, please email the maintainers directly.

We will endeavor to respond within 48 hours and provide a timeline for a patch. We ask that you maintain confidentiality until we have released a fix.
