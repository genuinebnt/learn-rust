Each task takes one time slot. Two runs of the same task need at least `n` other slots between them
(other tasks or idle slots). Slots run one after another, starting at 0.

- `least_interval(tasks, n)` returns the fewest slots that run every task, idle slots included.
- `schedule(tasks, n)` returns one such shortest schedule: `Some(task)` for a slot that runs a task, `None`
  for an idle slot. Any shortest valid schedule is accepted; it never ends with an idle slot.

Task ids can be any `char`, not only `A`–`Z`, and there can be thousands of different ones.
