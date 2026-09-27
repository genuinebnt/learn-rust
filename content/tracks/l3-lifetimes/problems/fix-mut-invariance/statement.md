Three signatures ask for `'static` where a shorter lifetime would do, and variance keeps the compiler
from quietly shortening it. Fix them so `all_names`, `shortest_line` and `apply` work on borrowed
text. `shorten` compiles already: it's the case where variance does let `'static` shrink.
