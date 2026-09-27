`WordFilter::new(words)` stores a list of lowercase words. `f(prefix, suffix)` returns the **largest index** `i`
such that `words[i]` starts with `prefix` and ends with `suffix`, or `None` if no word does.

Either part may be empty, and a word may appear more than once (the later index wins).
