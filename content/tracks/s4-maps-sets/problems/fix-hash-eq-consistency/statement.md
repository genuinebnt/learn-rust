`Username` compares case-insensitively, but a `HashSet<Username>` still counts `"Alice"` and
`"alice"` as different. Fix `Username` so `distinct` is right. Keep the case-insensitive comparison.
