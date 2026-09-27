Three functions box a generic `T` into a trait object and don't compile: nothing says `T` lives as
long as the object may be kept. Add the bounds they need, and no more: the tests pin borrowed data,
so don't require `'static` where `'a` will do. `pin_all` and `describe_each` compile already; work out
why before you touch them.
