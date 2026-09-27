`with_rollback(v, f)` lets `f` push to `v`. If `f` panics, `v` must be truncated back to its
original length before the panic continues; if `f` returns normally, its pushes stay.
