`after` and `lookup` compile, but tie their results to an input they don't borrow from, so the tests
(which pass temporaries there) don't compile. `Layered::get` doesn't compile at all: it returns a
global setting as if it were a local one. Fix all three with lifetimes alone. `or_default` is right as
it is.
