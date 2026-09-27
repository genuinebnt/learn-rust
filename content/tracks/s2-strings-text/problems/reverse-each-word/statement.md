Reverse the characters of each word, where words are the runs of non-whitespace. Keep every whitespace
character exactly where it was.

A combining mark (U+0300 to U+036F) belongs to the character before it and moves with it:
`"e\u{301}x"` (`éx`, written with a combining accent) becomes `"xe\u{301}"`. A mark at the very start of
a word has nothing to attach to, so it counts as a character on its own (with any marks that follow it).
