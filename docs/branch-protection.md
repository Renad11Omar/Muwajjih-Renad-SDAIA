# Branch protection checklist

The repository cannot self-configure GitHub branch protection from source control. After creating the repository, apply these settings to `main`:

- Require pull-request review: at least 1 approval.
- Require the CI checks to pass before merge.
- Disable force pushes.
- Disable branch deletion if your team wants stronger history protection.

The CI workflow is named `CI` and exposes the checks needed for lint/type-check/test/image-smoke validation.
