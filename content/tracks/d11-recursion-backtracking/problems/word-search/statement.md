`board` is a grid of ASCII letters, one `&str` per row. Return `true` if `word` can be traced on the board: start
on any cell, and step up, down, left or right from each letter to the next. A cell can be used at most once in a
word. Letters are case-sensitive.

The tests include adversarial boards, such as a board full of `A` and a word of many `A`s ending in a letter the
board doesn't have: plain backtracking takes far too long on those.
