The tempting design is `struct Parser { source: String, current: Option<&str> }`, where `current` points
into `source`. It can't be written in safe Rust: moving the struct would move the `String` value while
the reference still points at its buffer, and there's no lifetime to name for "my own field".

Instead, let the caller own the text. Implement `Parser<'a, T>` over a borrowed `&'a str`, generic over
a `Tokenize` strategy, and the two strategies:

- `Whitespace` splits on whitespace.
- `Comma` splits on `,`, trims each token, and skips empty ones.

`current` is the token most recently returned by `advance`: `None` before the first call and after
the end. Tokens must outlive the parser.
