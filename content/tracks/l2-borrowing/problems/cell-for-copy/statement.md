Write a doubly linked ring whose nodes live in an ordinary slice and point at each other with shared
references. Everything goes through `&Node`: linking, unlinking and counting visits all mutate through
shared borrows, with `Cell` and no `RefCell`, `Rc` or `unsafe`.
