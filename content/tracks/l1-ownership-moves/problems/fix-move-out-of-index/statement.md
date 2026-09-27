Every method here tries to move a value out of `self`, which it only borrows, so none of them compiles.
Fix each one without cloning, without allocating anything new, and without changing what it does.
