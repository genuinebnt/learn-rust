Fit `s` into `max_bytes` bytes. If it already fits, return it unchanged. Otherwise cut it at a
character boundary and append `…` (3 bytes), so the whole result is at most `max_bytes` bytes. If
there's no room even for `…`, return an empty string.
