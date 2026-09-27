A database keeps one slot per backend (a much-reduced PostgreSQL `PGPROC`): identity, timing,
application name, client address, current query, and the two fields every transaction reads,
`xid` and `xmin`. Every snapshot (`snapshot`) and every vacuum decision (`oldest_xmin`) scans all
slots for those two `u32`s, and with thousands of connections that scan dominates: each 248-byte
record costs a cache miss to read 8 bytes of it.

Split the representation so the scans read only what they need, with the API and behaviour
unchanged. In a release build, `oldest_xmin` over 131 072 connected backends must be at least
**4×** faster than the scan over the original records.

Transaction ids are `u32`s from 1 up (0 means none); they don't wrap here.
