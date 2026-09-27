**`sum_csv(line)`** adds up comma-separated integers. Fields are trimmed. A single trailing comma is
allowed (`"1,2,"`), but any other empty field is `Empty(n)`, with fields counted from 1. A field that
isn't an `i64` is `Bad(n, trimmed_text)`, and `Overflow` if the running total leaves `i64`. The first
problem from the left wins. An empty line sums to 0.

**`parse_log(line)`** splits `"<date> <time> <level> <message>"` on single spaces. The message is the
rest of the line, spaces and all, and may be empty or missing. Date, time and level must be non-empty.
`millis` is `Some(n)` when the message's last space-separated word is one or more ASCII digits followed
by `ms` and `n` fits in a `u64`. The message itself is kept whole.
