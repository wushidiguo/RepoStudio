# Security Policy

## Reporting a vulnerability

Please do **not** open a public issue for security vulnerabilities.

Instead, report them privately by emailing the maintainer or using GitHub's
[private vulnerability reporting](https://github.com/wushidiguo/RepoStudio/security/advisories/new)
flow. Include:

- A short description of the issue.
- Steps to reproduce, if possible.
- Affected versions or files.

We aim to acknowledge reports within a few days and to coordinate a fix and
advisory before public disclosure.

## Scope

RepoStudio clones and analyzes third-party repositories and, for some project
types, runs their code (dev servers, CLIs, example programs). The same caution
that applies to running untrusted code applies here: prefer generating videos
for repositories you trust, and run the pipeline in an isolated environment
when working with untrusted code.

The bundled installer downloads and executes third-party install scripts
(`codebase-memory-mcp`). These run with your user privileges; review what they
do before running them.
