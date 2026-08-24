# Triage Labels

The skills speak in terms of five canonical triage roles. This file maps those roles to the actual label strings used in this repo's issue tracker.

| Label in mattpocock/skills | Label in our tracker | Meaning                                  |
| -------------------------- | -------------------- | ---------------------------------------- |
| `needs-triage`             | `needs-triage`       | Maintainer needs to evaluate this issue  |
| `needs-info`               | `needs-info`         | Waiting on reporter for more information |
| `ready-for-agent`          | `ready-for-agent`    | Fully specified, ready for an AFK agent  |
| `ready-for-human`          | `ready-for-human`    | Requires human implementation            |
| `wontfix`                  | `wontfix`            | Will not be actioned                     |

When a skill mentions a role (e.g. "apply the AFK-ready triage label"), use the corresponding label string from this table.

Edit the right-hand column to match whatever vocabulary you actually use.

## Terminal state

The five roles above are all about *triage* — deciding who should pick an issue up.
None of them says the work is finished, so this repo adds one that does:

| Label in our tracker | Meaning                                                     |
| -------------------- | ----------------------------------------------------------- |
| `done`               | The work is finished and its acceptance criteria are checked |

It has no counterpart in mattpocock/skills; don't expect a skill to set it. Use it
when every checkbox on the issue is ticked and the resolution is written up under
`## Comments` — see `issue-tracker.md`. An issue that is merely *no longer being
worked on* is not `done`: that is `wontfix`, or back to `needs-triage`.
