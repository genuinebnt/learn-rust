`Span::enter(name, log)` records `"enter <name>"`, and dropping the span records `"exit <name>"`.
Exits must happen on every path: normal end of scope, early return, and panic.
