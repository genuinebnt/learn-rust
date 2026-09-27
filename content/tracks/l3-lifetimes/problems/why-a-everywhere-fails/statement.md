`Splitter` borrows the text and the separator with one lifetime `'a`. Callers can't keep a piece
after dropping the separator, though pieces only borrow from the text. Fix it so the tests compile.
The pieces must stay borrowed: don't copy them into `String`s.
