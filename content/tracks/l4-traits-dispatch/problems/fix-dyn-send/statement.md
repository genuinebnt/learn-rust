`dispatch_in_background` doesn't compile: `dyn Handler` cannot be sent between threads safely. Make a `Bus`
sendable. `Counter` must still share its count with the caller, now as `Arc<AtomicUsize>`.

Handlers that are `Send` but not `Sync` (a `Cell` inside, say) must still be accepted.
