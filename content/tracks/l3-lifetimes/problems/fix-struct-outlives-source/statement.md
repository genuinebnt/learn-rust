`excerpts`, `body_excerpt` and `biggest` each build an `Excerpt` from a `String` they made
themselves, which dies at the end of the function (or the loop turn) while the `Excerpt` still
borrows it. Fix them so every `Excerpt` borrows the caller's documents, with no copies. `biggest` also
has a bug the compiler can't see. `Excerpt::of` and `titles` are fine.
