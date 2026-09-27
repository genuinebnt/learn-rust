Two players take turns picking a number from 1 to `max_choosable`; a number can't be picked
twice. Each pick is added to a running total, and whoever makes the total reach at least
`desired_total` wins. Both play perfectly. Return whether the first player can force a win.
If the numbers add up to less than `desired_total`, nobody can win: return `false`. A
`desired_total` of 0 is already reached: return `true`.
