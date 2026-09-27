The tests call these functions one after another on the same `words`, and it doesn't compile: every
function takes `Vec<String>` by value. Give each the parameter (and return) type that says what it does
to the caller's words, and no more. `longest` returns `Option<&str>`.
