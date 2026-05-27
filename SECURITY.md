# Security Policy

## Supported Versions

Security fixes are prepared for the current `1.x` release line.

## Reporting Vulnerabilities

Report security issues privately through the repository security advisory flow or
by contacting the maintainers directly. Do not open public issues that include
secrets, exploit details, private documents, or credential material.

Include:

- affected Janusz version or commit;
- operating system and Python version;
- command or MCP method involved;
- minimal reproduction steps;
- expected and observed behavior.

## Secret Handling

Janusz treats source documents, generated JSON packages, generated skills, memory
files, and registry entries as local files under the user's control. Review
generated assets before sharing or installing them globally.

Do not place API keys, private keys, tokens, `.env` files, SSH material, cloud
credentials, or other secrets in source documents intended for packaging.

## MCP Filesystem Sandbox

`janusz mcp serve` confines tool file operations to a workspace root. The root is
the current working directory by default and can be configured with `--root` or
`JANUSZ_WORKSPACE_ROOT`.

The MCP layer resolves and normalizes paths, rejects traversal and symlink escapes,
denies common sensitive paths, enforces a default 10 MiB input size limit, and
sanitizes user-facing errors to avoid leaking host-specific paths. Resource
listings, including `janusz://packages`, use the same sensitive-path policy and
must not reveal `.env`, `.aws`, `.ssh`, `.git`, token, credential, or private-key
JSON paths.

MCP hosts should still run Janusz with the narrowest useful workspace root and a
least-privilege operating-system user.

## Dependency Security

Production release gates run `bandit -q -r src/janusz` and blocking `pip-audit`
with retry behavior. Normal unit tests do not require network access; dependency
advisory lookups do.

If advisory data cannot be fetched locally, run the release workflow in CI before
publishing any package.
