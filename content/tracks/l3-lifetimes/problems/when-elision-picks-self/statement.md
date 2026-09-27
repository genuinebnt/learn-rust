Three signatures here don't compile, or compile to something callers can't use, because elision picked
the wrong input for the output to borrow from. Fix them by writing the lifetimes that say what each
output really borrows. The tests keep results after the other inputs are gone. `define` and
`first_word` are right as they are.
