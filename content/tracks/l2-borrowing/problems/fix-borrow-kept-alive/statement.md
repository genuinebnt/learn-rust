`render` doesn't compile. Three borrows each outlive the place where you'd expect them to end: one is
used again after a mutation, one is carried into the next turn of a loop, and one belongs to a value
that still has work to do when it's dropped. Fix it without cloning, and keep `Batch` as it is.
