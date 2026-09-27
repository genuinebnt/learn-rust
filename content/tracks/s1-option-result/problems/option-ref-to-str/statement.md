The tests don't compile. They call this API the way real callers do: with string literals, with `Option<&str>`
from other code, and comparing results against `Some("...")`. Every signature here demands an owned `String`
(or a reference to one) that those callers don't have.

Fix the four signatures, and their bodies, so every test compiles and passes. Don't clone or allocate
anywhere except the `format!` that builds the greeting.
