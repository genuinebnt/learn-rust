Three closures return a slice of their argument, and none of them compiles, even the one that spells
out `-> &str`. The same bodies compile as `fn` items, and `Pipeline::add` accepts closures written
inline. Fix the three functions; `Pipeline` itself is fine.
