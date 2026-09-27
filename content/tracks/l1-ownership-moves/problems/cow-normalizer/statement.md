`normalize(s)` strips trailing whitespace and replaces each tab with four spaces (always four, not up to
a tab stop). It must allocate only when there's a tab to replace: a line that only needs trimming
comes back as a **borrowed slice** of `s`.

`with_newline(line)` makes sure a line ends with `'\n'`. A line that already does comes back as it was
(a borrowed one stays borrowed); an owned line gets the newline added to **its own buffer**, not a copy.
