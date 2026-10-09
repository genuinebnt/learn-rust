When a transaction changes a tuple for the first time, it must leave behind an undo log that a reader at an older snapshot can use. This stage writes the function that makes it from the tuple before the change and the tuple after: a **delta** that stores only the columns that differ. (The executors of module 4b call it; here you test it directly.)

## The task

In `src/execution/execution_common.rs`:

`generate_new_undo_log(schema, base_tuple: Option<&Tuple>, target_tuple: Option<&Tuple>, ts, prev_version) -> UndoLog`:

- `base_tuple` is the tuple **before** the change (`None`: it did not exist), `target_tuple` the tuple **after** (`None`: the change is a delete). `ts` is the timestamp of the base version and `prev_version` the log that was at the head of the chain.
- No base: the log has `is_deleted = true`, no modified columns, and an empty tuple (`Tuple::empty()`).
- No target (a delete): every column is modified and the tuple is the whole base tuple.
- Otherwise a column is modified when its value differs; two NULLs are equal (`same_value`, given), a NULL and a value differ. The log's tuple holds the base tuple's values of exactly the modified columns, built under `get_undo_log_schema(schema, &modified_fields)`.
- Always set `ts` and `prev_version`.

## Tests

- Changing some columns logs those columns, with their old values.
- The log keeps `ts` and `prev_version`.
- A delete logs every column; a tuple that did not exist logs a deleting log.
- NULL staying NULL is no change; NULL to a value and back is.
- A log applied to the target tuple with `reconstruct_tuple` gives the base tuple back.

## Syntax and methods

```rust
let modified_fields: Vec<bool> = (0..n).map(|i| match target_tuple {
    None => true,
    Some(t) => !same_value(&base.get_value(schema, i), &t.get_value(schema, i)),
}).collect();
let partial = get_undo_log_schema(schema, &modified_fields);
Tuple::new(&values, &partial)
```

## Notes

**Why store the old value.** The log answers "what was it *before* this change?", so it holds the base tuple's values. The most common mistake is to store the target's.

**Why a delta.** A tuple of 20 columns with one changed stores one value, not twenty; versions are cheap. The cost is the partial schema: a log is only meaningful together with the flags that say which columns it holds.

**Why a delete logs everything.** After the delete, the table's bytes are only a tombstone; the older readers need the whole tuple back, and it exists nowhere else. (An optimisation, not taken here: the table could keep the old bytes in place, but then readers would rely on a deleted tuple's data staying put, which breaks when its slot is reused.)

**"Did not exist" is a log too.** If the transaction inserts into the slot of a deleted tuple, older readers must still see "nothing there" and not the dead tuple's bytes. A log with `is_deleted` and no columns says exactly that.

## In BusTub

`execution_common.h`/`.cpp`:
```cpp
/**
 * @brief Generates a new undo log as the transaction tries to modify this tuple at the first time.
 * @param base_tuple The base tuple before the update, the one retrieved from the table heap. nullptr if the tuple is
 * deleted.
 * @param target_tuple The target tuple after the update. nullptr if this is a deletion.
 * @param ts The timestamp of the base tuple.
 * @param prev_version The undo link to the latest undo log of this tuple.
 */
auto GenerateNewUndoLog(const Schema *schema, const Tuple *base_tuple, const Tuple *target_tuple, timestamp_t ts,
                        UndoLink prev_version) -> UndoLog;
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `const Tuple *base_tuple` that may be `nullptr` | `Option<&Tuple>` |
| `if (v1.IsNull() && v2.IsNull()) ...; v1.CompareExactlyEquals(v2)` | `same_value(&a, &b)` (given) |
| `std::vector<bool> modified_fields` | `Vec<bool>` |

**Port rule:** a nullable pointer parameter is an `Option<&T>`; match on it instead of testing for `nullptr`.

## Learn more
- [`Option<&T>`](https://doc.rust-lang.org/std/option/enum.Option.html#method.as_ref) · [Delta compression of versions](https://www.vldb.org/pvldb/vol10/p781-Wu.pdf)

## Performance

Generating a log is linear in the number of columns plus one small tuple allocation. A wide table with a single-column update stores one value per version, which is the reason delta storage is used: the alternative copies the whole tuple for every update.

**Measure it.** For a 50-column table compare the byte length of the log for a one-column update with the length of the whole tuple.

## Hints

### Compare with NULL in mind

`compare_equals` on a NULL returns "unknown", never true; use `same_value` for every column or an unchanged NULL column is logged as modified.

### Build the partial tuple from the flags

Collect the base values of the flagged columns in order, then `Tuple::new(&values, &partial_schema)`. Do not build the full tuple and then try to trim it.

### The three cases are different shapes of the same log

No base, no target, both: decide the case first, then fill the same four fields.
