Build a prefix tree over lowercase ASCII words:

- `insert(word)` stores `word` (inserting it again changes nothing);
- `search(word)` is `true` if `word` itself was inserted;
- `starts_with(prefix)` is `true` if some inserted word starts with `prefix`.

A prefix of a stored word is not a stored word: after `insert("apple")`, `search("app")` is `false`.
The empty prefix walks nowhere, so `starts_with("")` is always `true`; `search("")` is `true` only after `insert("")`.
