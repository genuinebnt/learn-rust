`Editor` doesn't compile: three methods hold a borrow of one field (or try to move one) while calling
`note` or `apply`, which take all of `self`. Fix them without cloning anything and without changing
`note` or `apply`.
