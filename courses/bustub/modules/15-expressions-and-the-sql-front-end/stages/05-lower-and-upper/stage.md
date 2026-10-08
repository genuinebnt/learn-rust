`lower(name)` and `upper(name)`: the two string functions BusTub's shell knows. They are tiny, and they are where "a string is not an array of bytes" bites: the upper-case form of `ß` is `SS` (two characters), `É` is two bytes in UTF-8 but one letter, and a NULL string must stay a NULL string.

## The task

In `src/execution/expressions/string_expression.rs` (`StringExpressionType`, the constructor with its VARCHAR check, `evaluate`, `evaluate_join` and `to_string` are given):
- `compute(val: &str) -> String`: the lower- or upper-case form of `val`, chosen by `self.expr_type`;
- `result(val: &Value) -> Value`: given the argument's value, the VARCHAR value of the transformed string; the VARCHAR NULL stays NULL (`Value::null(TypeId::Varchar)`).

## Tests

- `lower` and `upper` of ASCII text, digits and punctuation, and of the empty string.
- Unicode letters change case too (`ÉCOLE` ↔ `école`, `ß` becomes `SS`, an emoji is left alone).
- NULL in, NULL out.
- The argument must be a VARCHAR when the node is built (`Execution` error); nested calls, columns in a row and in a join.
- `compute` is a plain function from strings to strings.

## Syntax and methods

```rust
s.to_lowercase()                 // String: Unicode-aware, may change the length
s.to_uppercase()
s.to_ascii_lowercase()           // ASCII only: bytes above 127 untouched (not what SQL's lower() does)
match val.as_str() { Some(s) => Value::varchar(&..), None => Value::null(TypeId::Varchar) }
```

## Notes

**Bytes are not letters.** `s.len()` is bytes; `"É".len()` is 2. Case conversion works on *characters* (Unicode scalar values) and some mappings change the number of characters (`"ß".to_uppercase() == "SS"`). C++'s `std::toupper` on a `char` handles only single bytes in the current locale; a correct port is `str::to_uppercase`, which implements the Unicode default mapping.

**The type check is up front.** `upper(1)` and `lower(true)` are *plan-time* errors: the constructor refuses a non-VARCHAR argument, so `compute` can only ever see strings. `select upper(1);` fails before any row is read; the test file `p0.02-function-error.slt` checks exactly that.

**Locale.** SQL's `lower` follows the database's collation (Turkish `I` lower-cases to `ı` in a Turkish locale). Rust's `to_lowercase` is locale-independent, which is also what PostgreSQL's `C` locale does for ASCII; BusTub documents no locale support.

## In BusTub

`string_expression.h`: `auto Compute(const std::string &val) const -> std::string { // TODO(student): implement upper / lower. return {}; }`: the stub students replaced, and the constructor `BUSTUB_ENSURE(GetChildAt(0)->GetReturnType().GetType() == TypeId::VARCHAR, "unexpected arg");`. The tests are `test/sql/p0.01-lower-upper.slt` and `p0.02-function-error.slt` (the C++ `StringExpression` was a project-0 warm-up).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::transform(s.begin(), s.end(), s.begin(), ::toupper)` (one byte at a time, current locale) | `s.to_uppercase()` (Unicode, a new `String`) |
| `std::string` holds bytes; its `size()` is bytes | `String` is UTF-8 and must stay valid: you cannot build it from arbitrary bytes by accident |
| `val.GetAs<char *>()` of a NULL varchar is a null pointer | `val.as_str()` is `None` for a NULL |
| `ValueFactory::GetVarcharValue(std::string)` | `Value::varchar(&str)` |

**Port rule:** `toupper`/`tolower` loops over `char` become `str::to_uppercase`/`to_lowercase`; a nullable C string pointer becomes an `Option<&str>`.

## Learn more
- [`str::to_lowercase`](https://doc.rust-lang.org/std/primitive.str.html#method.to_lowercase) · [Unicode case mapping FAQ](https://www.unicode.org/faq/casemap_charprop.html) · PostgreSQL [string functions](https://www.postgresql.org/docs/current/functions-string.html)

## Performance

`to_uppercase` allocates a new `String` and walks the text once with a table lookup per character: linear in the length, and the allocation dominates for short strings. `lower(upper(x))` allocates twice. An engine that cares applies `to_ascii_*` in place when it knows the data is ASCII.

**Measure it.** `upper` of a 20-byte ASCII string a million times with `to_uppercase` and with `to_ascii_uppercase`; then a string of `é` repeated.

## Hints

### Do not slice by bytes

Resist `s.bytes().map(...)`: it corrupts any multi-byte character. Let `to_lowercase` and `to_uppercase` do the work and just choose between them.

### The NULL case lives in `result`, not in `compute`

`compute` takes a `&str`: it cannot be given a NULL. Handle the NULL one level up, where the `Value` is.

### Equal after round trip

`upper(lower(x)) == upper(x)` is a property worth testing yourself for plain letters; it is *not* true for every Unicode string (`İ`), which is why the tests use fixed examples.
