`Reader`'s methods compile, but only one call can ever be made on a reader: after the first `take`,
`u16` or even `peek`, it stays borrowed for as long as its data. That's why `records`, which reads a
reader several times, doesn't compile, and its own signature does the same to its caller. Fix the
signatures so readers can be used normally; results must still borrow the data, not the reader.
