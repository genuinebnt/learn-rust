A trie that stores words with multiplicity:

- `insert(word)` adds one copy of `word`;
- `count_words_equal_to(word)` returns how many copies of `word` are stored;
- `count_words_starting_with(prefix)` returns how many stored copies start with `prefix` (every copy counts);
- `erase(word)` removes one copy and returns `true`, or returns `false` and changes nothing if `word` isn't stored.
