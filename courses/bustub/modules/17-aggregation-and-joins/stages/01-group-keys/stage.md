`select dept, sum(salary) from emp group by dept`: to group rows you need to decide when two rows belong to the **same group**, and to find a row's group fast, you need a hash table. A hash table asks its key type for two things: `Eq` (are these two keys the same?) and `Hash` (a number that is equal for keys that are equal). This stage defines both for a group key, the list of values of the `GROUP BY` expressions. It looks small and is where SQL's NULL rules meet Rust's hashing contract.

## The task

In `src/execution/executors/aggregation_executor.rs`, for `AggregateKey { group_bys: Vec<Value> }` (the helper `canonical(&Value)` turns a value into a form on which "same group" is plain `==`):
- `PartialEq::eq`: same number of values, and every pair has equal `canonical(..)` forms;
- `Hash::hash`: feed the `canonical` form of every value to the hasher, in order, so that keys that are equal hash alike.

## Tests

- Equal keys are equal and have equal hashes; different strings or numbers are different.
- Two NULLs are the **same** group (a NULL is a NULL whatever its type), but NULL is not 0.
- Equal integers of different widths (`tinyint 5`, `bigint 5`) are the same group.
- The number of values matters (`[1]` is not `[1, 1]`; the empty key equals the empty key).
- A decimal `0.0` and `-0.0` are one group.
- Keys work as `HashMap` keys (counting 1, NULL, 1, NULL, 2, `bigint 1` gives three groups).

## Syntax and methods

```rust
impl PartialEq for AggregateKey { fn eq(&self, other: &Self) -> bool { .. } }
impl Eq for AggregateKey {}                                  // given: a marker that eq is an equivalence
impl Hash for AggregateKey { fn hash<H: Hasher>(&self, state: &mut H) { canonical(v).hash(state); } }
self.group_bys.iter().zip(&other.group_bys).all(|(a, b)| canonical(a) == canonical(b))
```

## Notes

**Two notions of equal.** In a `WHERE`, `NULL = NULL` is unknown. In a `GROUP BY`, all NULLs form one group (SQL calls this *not distinct*). BusTub's C++ key does something else: its `operator==` returns false unless `CompareEquals == CmpTrue`, so keys with NULLs never match and each NULL row would be its own group. The test file even warns: "if you see a seg fault here, it is likely because you are not currently supporting group by on columns with nulls". This course uses the SQL rule; the tests pin it.

**The contract.** If `a == b` then `hash(a) == hash(b)`. Implementing `eq` on `canonical` forms and `hash` on the *same* forms makes it hold by construction. If `eq` says `tinyint 5 == bigint 5` while `hash` fed the raw bytes, a `HashMap` would put them in different buckets and silently miss a match.

**Why `canonical` exists.** `Value` holds an `f64` (not `Hash`, not `Eq`), integers of four widths, and a NULL with a type. `canonical` maps each to a tuple of simple types: integers widen to `i64`, a decimal contributes its bit pattern (with `-0.0` mapped to `0.0`), a NULL is `(0, ...)` whatever its type.

## In BusTub

`aggregation_plan.h`: `struct AggregateKey { std::vector<Value> group_bys_; auto operator==(const AggregateKey &other) const -> bool { for (...) { if (group_bys_[i].CompareEquals(other.group_bys_[i]) != CmpBool::CmpTrue) { return false; } } return true; } };` and `template <> struct hash<bustub::AggregateKey> { ... if (!key.IsNull()) { curr_hash = bustub::HashUtil::CombineHashes(curr_hash, bustub::HashUtil::HashValue(&key)); } ... }`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `namespace std { template <> struct hash<AggregateKey> {...}; }` plus `operator==` | `impl Hash for AggregateKey` plus `impl PartialEq` and `impl Eq` |
| `HashUtil::CombineHashes(a, b)` | `value.hash(&mut hasher)` per value: the hasher mixes |
| nothing stops `==` and `hash` from disagreeing | the `Hash`/`Eq` contract is documented, and `canonical` makes it structural |
| `f64` keys compile silently | `f64` is not `Hash`/`Eq`, so you must decide what equality of floats means |

**Port rule:** write `eq` and `hash` from one canonical form of the key.

## Learn more
- [`Hash`](https://doc.rust-lang.org/std/hash/trait.Hash.html) · [`Eq`](https://doc.rust-lang.org/std/cmp/trait.Eq.html) · PostgreSQL [`IS NOT DISTINCT FROM`](https://www.postgresql.org/docs/current/functions-comparison.html)

## Performance

Every input row of an aggregation computes one key and one hash: the key's `Vec<Value>` is allocated, each value hashed. A real engine hashes the raw column bytes without building `Value`s. The `canonical` form borrows the string (`&str`) rather than copying it, so hashing a VARCHAR key does not allocate.

**Measure it.** Build 1,000,000 `AggregateKey`s of one integer and insert them into a `HashMap`; then of one 20-byte string.

## Hints

### Hash only what `eq` compares

If `eq` ignores something (the type of a NULL, the width of an integer), `hash` must too: both go through `canonical`.

### The empty key is a real key

`SELECT count(*) FROM t` has no `GROUP BY`: the group key is the empty list, and all rows hash to the same bucket. Do not special-case it away.

### Do not use `==` on `Value`

`Value`'s derived equality is about the Rust enum (`Integer(5) != BigInt(5)`, `Null(Integer) != Null(Varchar)`). SQL value equality lives in the compare methods (NULL answers unknown). The grouping rule is a third thing; that is why it has its own function.
