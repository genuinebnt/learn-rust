`Span::enter(name, log)` records `"enter <name>"`, and dropping the span records `"exit <name>"`, on
every path: normal end of scope, early return, and panic.

`span.finish(status)` ends a span explicitly, recording `"exit <name>: <status>"` **instead of** the plain
exit. Each span records exactly one exit.
