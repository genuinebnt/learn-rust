`Header` and `Body` are views: each bundles `&mut` borrows of some of `Document`'s fields. Write the
methods that make them and use them, and `hashtags`, which reads the body while it adds tags to the
header. Two views made by two `&mut self` calls can't be alive together; `split` has to make both.
