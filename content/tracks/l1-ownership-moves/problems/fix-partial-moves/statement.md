Three functions, three different ownership errors. Fix them without cloning anything and without
`unsafe`. Several moves in `route` are fine as written; keep them.

`route_pooled` must still give the pool slot back: `Pooled`'s `Drop` has to run.
