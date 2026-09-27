`Registry::id` runs on every request and allocates a `String` each time. Make it look the name up without allocating.
