`WHERE x = 5` asks a value whether it equals another. In SQL the answer is not a boolean: it is **true, false or unknown**. If either side is NULL the comparison is *unknown*, and a `WHERE` keeps only the rows for which the condition is *true* (not those where it is false, and not those where it is unknown). This is **three-valued logic**, and getting it wrong is the classic SQL bug: `WHERE x != 5` does not return rows where x is NULL, and `WHERE x = NULL` returns nothing.

This stage implements the six comparisons on `Value`, returning `CmpBool::{True, False, Null}`, including the conversions that make `'32' = 32` true.

> [!CHECK] What does `NULL = NULL` evaluate to in SQL, what does `WHERE x = NULL` return, and how do `GROUP BY` and `ORDER BY` treat two NULLs? Say how your `compare` result type has to represent this.
> ||`NULL = NULL` is NULL (unknown), not true, so `WHERE x = NULL` returns no rows (that is what `IS NULL` is for). `GROUP BY` puts all NULLs in one group and `ORDER BY` treats them as equal, which is why a comparison needs a third answer beside true and false.||
>
> - What would `NOT (a = b)` return if `a = b` were just false?
> - A row passes a filter only for which result?
> - Which operations need "same" and which "equal"?

## The task

In `src/types/value.rs` implement the comparison core `compare(&self, other) -> Result<Option<Ordering>>` and the public wrappers `compare_equals`, `compare_not_equals`, `compare_less_than`, `compare_less_than_equals`, `compare_greater_than`, `compare_greater_than_equals` (each `Result<CmpBool>`; the shared `cmp_with` is given) and `compare_exactly_equals(other) -> bool`:
- types that `check_comparable` refuses are an error ("type error");
- a NULL on either side: `None` from `compare`, so `CmpBool::Null`;
- two **numbers** compare by value across types (integers exactly; anything involving a decimal as `f64`);
- a **number and a string**: the string is converted to the *number's type* first (`5 < '12'` is true); a **string and anything**: the other value is converted to text first and the strings compare **bytewise** (`'5' > 12` is true: as text `"5" > "12"`);
- a **boolean** and a string: the string is converted to a boolean; two timestamps compare as numbers;
- `compare_exactly_equals`: two NULLs are equal (for grouping and hashing); otherwise `compare_equals == True`, an error counts as false.

## Tests

- Numbers across types (a tinyint against a bigint, an integer against a decimal) in all six comparisons.
- A NULL on either side gives `Null`, not `False`, for every operator and several types.
- Strings: bytewise order, a prefix is smaller, upper case sorts before lower; the BusTub case `'32' = 32` both ways, the two directions of "convert to what?"; booleans, incomparable types, timestamps; `compare_exactly_equals`.

## Syntax and methods

```rust
use std::cmp::Ordering;
a.as_bytes().cmp(b.as_bytes())                       // Ordering::{Less, Equal, Greater}, bytewise
ord.is_lt()  ord.is_le()  ord.is_eq()  ord.is_ne()  // Ordering -> bool
fn cmp_with(&self, other: &Value, f: impl Fn(Ordering) -> bool) -> Result<CmpBool>   // one core, six operators
```

## Notes

**One comparison, six answers.** Implement `compare` once and derive the six operators from its `Option<Ordering>`: `None` is always `Null`; `Some(o)` is `o.is_eq()`, `o.is_lt()`, and so on. BusTub writes each operator out per type (hundreds of lines); the three-valued rule (NULL gives NULL) is the same everywhere, so it belongs in one place.

**Which side converts?** The rule that surprises: with a number on the left and a string on the right the *string* converts (to the number's type), but with a string on the left *everything* converts to text. So `5 < '12'` compares 5 with 12 (true) while `'5' < 12` compares "5" with "12" (false). The tests pin both.

**`Option<bool>` is the same idea.** `CmpBool` is a three-valued boolean; the standard library's `Option<bool>` is another. SQL's `AND`/`OR`/`NOT` over them (module 3b) follow the same table: `false AND NULL` is false, `true AND NULL` is NULL.

## In BusTub

`IntegerType::CompareEquals` and siblings (`if (left.IsNull() || right.IsNull()) { return CmpBool::CmpNull; } INT_COMPARE_FUNC(==);`), `VarlenType` (`VARLEN_COMPARE_FUNC`, `TypeUtil::CompareStrings`: "memcmp ... if (ret == 0 && len1 != len2) { ret = len1 - len2; }") and `Value::CompareExactlyEquals` ("You will likely need this in project 4...").

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `enum class CmpBool { CmpFalse, CmpTrue, CmpNull }` and `GetCmpBool(bool)` | `enum CmpBool { False, True, Null }` and `CmpBool::from_bool` |
| six virtual methods per type, each with a copy of the NULL check | one `compare` returning `Option<Ordering>`, six one-line wrappers |
| `memcmp` plus a length tie-break | `[u8]::cmp` (lexicographic with the same tie-break) |
| `assert(left.CheckComparable(right))` (compiled out in release builds) | an `Err` that is always checked |

**Port rule:** collapse per-operator duplication into a core that returns an ordering, and derive the operators from it.

## Learn more
- [`Ordering`](https://doc.rust-lang.org/std/cmp/enum.Ordering.html) · [`Ord::cmp`](https://doc.rust-lang.org/std/cmp/trait.Ord.html#tymethod.cmp) · [Three-valued logic](https://en.wikipedia.org/wiki/Three-valued_logic) · PostgreSQL [comparison operators and NULL](https://www.postgresql.org/docs/current/functions-comparison.html)

## Performance

Comparing two integers of the same type should be a couple of instructions; this core goes through `check_comparable`, two `is_null` tests and a `match`, so it is several times slower than `a < b` on `i32`. Executors (module 3b) therefore avoid calling it per row where they can: they resolve types once at plan time. If you profile a scan later, this is where the time goes; a specialised fast path for "both `Integer`" is the classic optimisation.

Comparing strings is a `memcmp`: linear in the common prefix, so comparing long strings that share a long prefix is where it hurts (and why databases compare hashes or prefixes first when they can).

**Measure it.** Compare 100 million `compare_less_than` calls on integers against raw `i32` comparisons, then add a fast path for two `Integer` values and measure again.

## Hints

### The order of the checks decides the answer

Check comparability first (an error even for a NULL), then NULL, then convert, then compare. A test compares a NULL with an incomparable type and expects the error, and another compares NULLs of comparable types and expects `Null`.

### Convert, then call yourself

For `number vs string`, cast the string to the number's type and call `compare` again with the converted value; the recursion lands in the numbers-only branch. For `string vs anything`, cast the other side to text; for `boolean vs string` cast the string to boolean.

### `partial_cmp` can fail; do not let NaN panic

`f64::partial_cmp` returns `None` for NaN. A comparison with NaN in a database is rare; decide what the engine does (the reference treats it as equal) and test it, rather than unwrapping.
