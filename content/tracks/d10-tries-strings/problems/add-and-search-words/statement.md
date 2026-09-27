`WordDictionary` stores lowercase words.

- `add_word(word)` stores `word`;
- `search(pattern)` is `true` if some stored word matches `pattern`, where `.` matches any one letter.

The whole word must match: `"b.."` matches `"bad"` but not `"ba"` or `"bads"`.
