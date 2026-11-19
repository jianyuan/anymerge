# Stability

anymerge is at version 0.x. Semantic versioning makes no promises before 1.0, so this page sets out the ones anymerge makes.

- A breaking change bumps the minor version, for example from 0.1 to 0.2, and the release notes list it.
- A patch release, for example from 0.1.0 to 0.1.1, only fixes bugs and never breaks working code.
- A deprecated function, class or argument keeps working for at least one minor release and raises a `DeprecationWarning` while it does.

Changing a default counts as a breaking change. That includes how a field without a reducer merges and what happens to update keys the base doesn't declare.

## Public API

The public API is every name exported from these modules:

- `anymerge`
- `anymerge.adapters`
- `anymerge.exceptions`
- `anymerge.models`
- `anymerge.reducers`
- `anymerge.types`

Modules whose names start with an underscore, such as `anymerge._merger`, are internal and can change in any release. So can error message text. Catch the exception class instead of matching its message.

To pin a version that won't break, use a compatible-release specifier such as `anymerge~=0.1.0`, which allows 0.1.x but not 0.2.
