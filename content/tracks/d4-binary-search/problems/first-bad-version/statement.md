Versions `1..=n` are good up to some point and bad after it. Using as few calls to `is_bad` as possible
(at most 33), return the first bad version, or `None` if none is bad. `n` can be `u32::MAX`.
