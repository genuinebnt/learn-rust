Return whether the pattern `p` matches all of `s`. In `p`, `.` matches any single
character, and `x*` (any character or `.` followed by `*`) matches zero or more copies of
`x`. Every other character matches itself. Characters are Unicode scalar values. Every `*`
in `p` follows a character that isn't `*`.
