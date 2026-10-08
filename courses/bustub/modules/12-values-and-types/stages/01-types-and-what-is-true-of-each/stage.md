Module 3 is the query engine, and everything it moves around is a **value**: the `5` in `WHERE x > 5`, a name in a result row, a NULL. Before executors, tuples or tables there has to be an answer to *what is a value, and what can you do with one?* This module builds BusTub's type system in Rust. This first stage is the type *names*: which SQL types exist, how many bytes each takes, and which can be converted from which.

It is also the course's first look at three Rust tools you will use for the rest of module 3: an **enum** to say "one of these types", `match` to say what is true of each, and `Result` with an exception type for things that go wrong.

**Where this fits.** BusTub's `Type` class has one subclass per SQL type; its static functions (`GetTypeSize`, `TypeIdToString`, `IsCoercableFrom`) are facts about a type as a whole. Here they are methods of the `TypeId` enum.

## The task

In `src/types/type_id.rs` implement for `TypeId` (the enum is given, with `Invalid`, `Boolean`, `TinyInt`, `SmallInt`, `Integer`, `BigInt`, `Decimal`, `Varchar`, `Timestamp`):
- `type_size() -> Result<u64>`: 1 byte for `Boolean` and `TinyInt`, 2 for `SmallInt`, 4 for `Integer`, 8 for `BigInt`, `Decimal` and `Timestamp`, **0** for `Varchar` (its bytes are not in the fixed part of a tuple); `Invalid` is an `UnknownType` error (`src/common/exception.rs` is given);
- `type_id_to_string()`: `"INVALID"`, `"BOOLEAN"`, ... the upper-case SQL names;
- `is_coercable_from(other) -> bool`: can a value of type `other` be converted to this type? `Invalid` accepts nothing; `Boolean` accepts anything; the numeric types (`TinyInt` to `Decimal`) accept the numeric types and `Varchar`; `Timestamp` accepts `Varchar` and itself; `Varchar` accepts every type but `Invalid`.

## Tests

- Sizes of every type, and `Invalid` has none (an `UnknownType` error); the names.
- The whole 9 x 9 coercion table, checked cell by cell; a type is coercable from itself except `Invalid`.

## Syntax and methods

```rust
match self {
    TypeId::Boolean | TypeId::TinyInt => Ok(1),                       // or-patterns share an arm
    TypeId::Invalid => Err(Exception::new(ExceptionType::UnknownType, "Unknown type.")),
    /* ... */
}
matches!(other, TypeId::TinyInt | TypeId::SmallInt)                   // a match that answers true or false
```

## Notes

**An enum is a closed set.** Add a tenth type and every `match` that names the old nine stops compiling until you handle it: the compiler finds every place the new type matters. In BusTub's C++ the same fact lives in a `switch` that quietly falls through `default`.

**`Result` instead of `throw`.** `type_size` can fail for `Invalid`, and the failure is part of its signature: the caller must look at it. C++ would `throw Exception(ExceptionType::UNKNOWN_TYPE, ...)` and let it unwind to whoever catches it; here the error is an ordinary value.

**Why a table of coercions.** Later stages do not ask "is this cast legal?" ad hoc; they consult one agreed table. BusTub's table has quirks (a `Boolean` accepts anything; the numeric types accept `Varchar` though `Timestamp` accepts it only from `Varchar`), which the tests pin exactly.

## In BusTub

`type.cpp`: `Type::GetTypeSize` ("case BOOLEAN: case TINYINT: return 1; ... case VARCHAR: return 0; ... throw Exception(ExceptionType::UNKNOWN_TYPE, "Unknown type.")"), `Type::IsCoercableFrom` and `Type::TypeIdToString`. The `type_test` boss calls them on every type.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `enum TypeId { INVALID = 0, BOOLEAN, TINYINT, ... }` (an int in disguise) | `enum TypeId` (a real type; `as u8` only when you need the number) |
| `switch (type_id) { case BOOLEAN: ... default: throw ...; }` | `match` with no `default`: it must cover every variant |
| `throw Exception(ExceptionType::UNKNOWN_TYPE, "...")` | `Err(Exception::new(ExceptionType::UnknownType, "..."))` |

**Port rule:** a C++ function that can throw becomes a Rust function that returns `Result`; the `throw` becomes `Err(..)` and every caller decides what to do with it.

## Learn more
- [The Rust Book: enums and `match`](https://doc.rust-lang.org/book/ch06-00-enums.html) · [`Result`](https://doc.rust-lang.org/std/result/index.html) · [`matches!`](https://doc.rust-lang.org/std/macro.matches.html)

## Performance

All three functions are a `match` over a small enum: a jump table or a few comparisons, no allocation, constant time. `type_size` is called for every column of every tuple that is built or read, so keeping it a plain `match` (not a hash lookup, not a `Vec` search) matters later.

**Measure it.** Time 100 million calls to `type_size` over a cycling array of types and compare it with a `HashMap<TypeId, u64>` lookup.

## Hints

### Write the table down first

For `is_coercable_from`, draw the 9 x 9 grid on paper from the rules in the task, then turn each row into one `match` arm. A wrong cell shows up as a test named after the pair.

### Which arms can share a body?

`Boolean | TinyInt` share a size; the five numeric types share a rule. Use or-patterns and `matches!` so the rule is stated once; copy-pasted arms are where a table drifts out of agreement with itself.

### Do not invent a size for `Invalid`

`Invalid` is not a type with size zero; it is the absence of a type. Returning `Ok(0)` would let a bug (an uninitialised type) look like a legitimate `VARCHAR`.
