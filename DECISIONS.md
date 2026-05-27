# Decisions

## ADR-001: Keep Optional AI/Schema Features Experimental for 1.0

- Decision: Keep AI/schema generation outside the stable 1.0 compatibility
  contract.
- Context: `schema generate-ai` is now wired and offline-tested with fakes, but
  real provider behavior still depends on external credentials and network.
- Alternatives considered:
  - Promote AI/schema generation to stable.
  - Disable the command entirely.
- Reason: Keeping the command experimental preserves usefulness without
  overclaiming production stability.
- Risk: Users may expect provider-backed behavior to be stable.
- Reversal plan: Promote after provider configuration, retry behavior, error
  taxonomy, and integration tests are separately hardened.

## ADR-002: Share MCP Sensitive Path Policy Across Tools and Resources

- Decision: MCP resource listings must use the same sensitive path policy as MCP
  file tools.
- Context: Package discovery previously filtered only a few generated
  directories and could reveal sensitive JSON paths.
- Alternatives considered:
  - Maintain separate filtering for resource listings.
  - Hide package discovery entirely.
- Reason: A single policy reduces security drift and keeps package discovery
  useful for orchestrators.
- Risk: Overly broad filename markers can hide legitimate JSON packages with
  words such as `token` or `credential`.
- Reversal plan: Replace the denylist with a configurable policy if real safe
  packages are blocked.

## ADR-003: Use Local Git Commits as Autonomous Checkpoints

- Decision: Autonomous maintainer work should create local commits after coherent
  verified task batches.
- Context: Long-running loops need durable checkpoints and safe continuation.
- Alternatives considered:
  - Leave all changes uncommitted until user review.
  - Squash only at the end of a session.
- Reason: Local commits are reversible checkpoints and do not publish anything.
- Risk: Commits may need later squash/rewording before merging.
- Reversal plan: Maintainers can amend, squash, or cherry-pick local commits.

## ADR-004: Keep MCP Resource Listings Deterministic

- Decision: MCP resource discovery should return globally sorted,
  workspace-relative paths.
- Context: Orchestrators may cache or diff MCP resource output, and filesystem
  traversal order is not a stable API.
- Alternatives considered:
  - Preserve filesystem order.
  - Sort only filenames per directory.
- Reason: Global sorting gives predictable output and makes resource consumers
  easier to test.
- Risk: Collecting before limiting can be slower in huge workspaces.
- Reversal plan: Replace with a bounded heap or paginated resource API if large
  workspace performance becomes a problem.

## ADR-005: Hide Non-File JSON Paths From MCP Package Resources

- Decision: MCP JSON package discovery reports only resolved paths that are
  files.
- Context: Mutation-driven tests exposed that a dangling `*.json` symlink could
  be surfaced as a package-like entry even though its target did not exist.
- Alternatives considered:
  - Report symlink paths without checking target existence.
  - Raise an error for dangling symlinks.
- Reason: Resource listings should be robust and should not advertise paths that
  cannot be read as package files.
- Risk: A legitimate package represented by an unusual filesystem object will be
  hidden.
- Reversal plan: Add an explicit opt-in resource mode if a real use case needs
  non-regular package entries.

## ADR-006: AI Skill Builder Produces Drafts Only

- Decision: Keep AI skill generation experimental and require the model to
  return only a strict structured draft.
- Context: The stable Janusz skill pipeline is deterministic and should not be
  replaced by provider-generated files.
- Alternatives considered:
  - Let the model write `SKILL.md` directly.
  - Reuse `janusz skill --use-ai` and change its existing meaning.
- Reason: A draft-only provider keeps file writes, validation, linting, and
  scoring under Janusz control while preserving the deterministic CLI.
- Risk: Users may expect `janusz skill ai` to be as stable as `janusz skill`.
- Reversal plan: Promote the command only after provider behavior, retry policy,
  and integration testing are hardened separately.
