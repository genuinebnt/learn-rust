Render `template`, replacing `{name}` with `vars[name]`. `{{` and `}}` are a literal `{` and `}`.

Errors carry the byte offset where they start:

- `Unknown(name)` for a name not in `vars`.
- `Unclosed(pos)` for a `{` with no closing `}`.
- `StrayBrace(pos)` for a lone `}`.
