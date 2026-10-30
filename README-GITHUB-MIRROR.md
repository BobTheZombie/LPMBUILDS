# LPMBUILDS GitHub mirror

GitLab is the canonical source of package recipes:
https://gitlab.com/lpm-org/packages

GitHub Actions mirrors tracked files from GitLab's default branch, replacing stale
GitHub package files while preserving only this README, .github, and
tools/github-mirror. Do not add packages only to this GitHub repository:
submit them upstream to GitLab.

The workflow then updates Plasma Workspace **6.8.1** by adding dependencies
only if a non-placeholder NAME or PROVIDES declaration exists in the mirrored
GitLab index, enabling the SDDM Wayland greeter when safely possible. It
emits PLASMA-DEPENDENCY-AUDIT.md plus dependency-audit-output.txt with missing
packages and placeholder-only providers. It does not invent, silently remove,
or pretend to have compiled a missing dependency.

Run manually using Actions > Synchronize GitLab LPM package recipes >
Run workflow. Changes to the workflow and synchronization tools also trigger a run. Automatic daily sync is disabled until the missing Plasma requirements are addressed.

Limitations:
- GitLab must be publicly readable by GitHub Actions.
- Repository settings must grant Actions contents:write and allow bot pushes.
- A NAME/PROVIDES audit verifies package naming, not ABI, buildability, or
  installed CMakeConfig files.
- An unresolved dependency is documented and must be implemented/repaired.
- GitLab's Plasma version is preserved when it is not 6.8.1.

The GitHub-specific mirror files are intentionally excluded from GitLab sync.
