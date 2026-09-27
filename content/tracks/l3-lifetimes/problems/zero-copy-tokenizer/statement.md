`Tokenizer` yields `Token`s borrowed from the source: identifiers (ASCII letter or `_`, then letters,
digits, `_`), numbers (ASCII digits) and single punctuation characters (any other non-whitespace
character). Whitespace separates tokens.

`longest_ident` returns the longest identifier from any token iterator (the first one on a tie). It
must work on tokens that outlive the tokenizer.
