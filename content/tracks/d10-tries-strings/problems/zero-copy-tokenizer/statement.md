Write a lexer for a small language. `Lexer::new(src)` is an iterator of `Result<(Token, span), LexError>`,
where `span` is the token's byte range in `src`.

- Whitespace (any Unicode whitespace) and `//` comments, up to the end of the line, are skipped.
- `Ident`: an ASCII letter or `_`, then ASCII letters, digits and `_`.
- `Int`: a run of ASCII digits. `12ab` is `Int("12")` then `Ident("ab")`.
- `Str`: `"…"`, holding any Unicode, newlines included. Escapes are `\\`, `\"`, `\n` and `\t`. The token holds the
  contents without the quotes: **borrowed** from `src` when there is no escape, owned only when one had to be
  resolved. Its span includes the quotes.
- `Op`: the **longest** operator that matches: `== != <= >= -> => && || ::`, else one of `+ - * / % = < > ! & | : ; , . ( ) { } [ ]`.

Errors: `Unexpected { at, ch }` for a character that starts no token, `BadEscape { at }` (the backslash) for an
unknown escape, `UnterminatedString { at }` (the opening quote) when the input ends inside a string. After an
error, or the end, `next` returns `None` forever.

Tokens borrow from `src`, not from the lexer, and may outlive it.
