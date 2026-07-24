## Overview

### What changed?

Describe the change in one or two sentences. Include the user-facing outcome, not just the implementation detail.

### Why is it needed?

Explain the problem, limitation, or opportunity this PR addresses.

### Related links

- Issue or discussion:
- Release note entry:
- Documentation update:

## Scope

### Affected areas

- [ ] Public API
- [ ] CLI
- [ ] Parser / repair behavior
- [ ] Tokenizer
- [ ] Error handling
- [ ] Documentation
- [ ] Packaging / release
- [ ] Tests / CI
- [ ] GitHub workflow
- [ ] Citation / metadata
- [ ] Other

### Compatibility impact

- [ ] Backward compatible
- [ ] Behavior change only
- [ ] Potentially breaking
- [ ] Not sure

### Release classification

- [ ] Patch-level fix
- [ ] Minor backward-compatible feature
- [ ] Major breaking change
- [ ] Documentation-only change

## Validation

Check the items that you actually ran and adjust commands if your change needs something different.

- [ ] `ruff check .`
- [ ] `pytest`
- [ ] `mypy src/laga`
- [ ] `python -m build`
- [ ] Manual CLI smoke test
- [ ] Manual import / runtime smoke test

### Evidence

Paste the most relevant output, screenshot, or before/after example here.

## Risk Review

### What could break?

List the most likely regressions, edge cases, or user-visible side effects.

### Mitigations

Describe tests, safeguards, or docs you added to reduce that risk.

### Follow-up work

- [ ] None
- [ ] Additional tests needed
- [ ] Docs follow-up needed
- [ ] CI / release follow-up needed
- [ ] Migration note needed

## Review Notes

### Suggested review focus

Tell reviewers what to pay attention to: API shape, edge cases, release impact, readability, or compatibility.

### Notes for maintainer

Use this for anything that should be considered before merge, release, or tagging.

## Checklist

- [ ] I linked the related issue or discussion.
- [ ] I described the change in user-facing terms.
- [ ] I verified the relevant tests or checks.
- [ ] I considered compatibility and release impact.
- [ ] I updated docs, changelog, or templates if needed.
- [ ] I checked that CI and release workflows are not affected unexpectedly.
