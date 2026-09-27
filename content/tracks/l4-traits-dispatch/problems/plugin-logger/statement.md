Build composable loggers over `Box<dyn Logger + Send + Sync>`:

- `PrefixLogger` prepends its prefix to each message and passes it on.
- `LevelFilter` passes on only messages at or above `min`.
- `Tee` sends each message to all its sinks, in order.
- `Arc<L>` is a `Logger` too, so one sink can sit under several wrappers.

`flush` has an empty default, but every wrapper must pass it on. Loggers get shared across threads.
