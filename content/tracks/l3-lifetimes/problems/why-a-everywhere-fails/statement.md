`Splitter` borrows the text and the separator with one lifetime `'a`, and its pieces are `&'a str`.
So a piece seems to borrow the separator too, and `split_lines`, whose separator is a local
`String`, can't return its pieces. Fix `Splitter` so pieces borrow only the text. Don't touch
`split_lines`, and keep the pieces borrowed (no copies).
