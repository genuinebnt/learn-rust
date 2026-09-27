None of these compiles. Fix the three signatures, with the lifetimes callers need: the tests keep
`longest_of`'s result after the slice of words is gone, and store lines of their own into
`keep_longest`'s `best`. No copying.
