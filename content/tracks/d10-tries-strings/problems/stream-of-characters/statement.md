`StreamChecker::new(words)` stores a list of lowercase words. Letters then arrive one at a time through `query(letter)`,
which returns `true` if some word is a suffix of the stream so far, that is, the stream ends with that word.
