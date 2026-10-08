From here on the course runs SQL. You type `select lower(name) from people where id = 3;` and a pipeline you did not have to write turns the text into a **plan**: a tree of operators (scan, filter, projection, ...). The part of the plan that computes with values, `lower(name)`, `id = 3`, `a + b`, is an **expression tree**, and writing the nodes of that tree is this module's job.

```text
  SQL text  →  parser  →  binder  →  planner  →  optimizer  →  executors  →  rows
              (syntax)   (names →   (a tree of    (rewrites    (pull tuples,
                          objects)   operators)    the plan)    evaluate expressions)
```

Everything left of "executors" is **given code**, a port of BusTub's `binder/`, `planner/` and `optimizer/` (BusTub parses with PostgreSQL's parser; this course has its own small parser in `src/sql/`, so the project needs no dependencies). You can already try it: `cargo run --bin bustub_shell`, then `select 1 + 2;` or `explain select upper(day_of_week) from __mock_table_schedule;`. Until you write the expressions, the answers are `not yet implemented` panics, and that is the work of this module.

This stage is the leaves of the tree: a **constant** (`5`, `'hello'`) and a **column value** (`the third column of the row`).

## The task

In `src/execution/expressions/` (the `Expression` trait in `abstract_expression.rs` is given):
- `ConstantValueExpression::evaluate` and `evaluate_join`: return the literal, whatever the tuple is;
- `ColumnValueExpression::evaluate`: the value of column `col_idx` of the tuple, read with the tuple's schema (module 3b's `Tuple::get_value`);
- `ColumnValueExpression::evaluate_join`: a join has **two** input tuples, a left and a right, each with its own schema; `tuple_idx` says which one this column belongs to (0 = left, anything else = right).

## Tests

- A constant (an integer, a string, a NULL) is itself for any tuple, in `evaluate` and in `evaluate_join`.
- A column value reads the right column of a row, including a NULL and a VARCHAR.
- In a join, `tuple_idx` picks the left or the right tuple, and each is read with its own schema.
- Expressions describe themselves (`#0.3`, `5`) and know their return type.

## Syntax and methods

```rust
pub trait Expression: Send + Sync + Debug {
    fn evaluate(&self, tuple: &Tuple, schema: &Schema) -> Result<Value>;
    fn evaluate_join(&self, l: &Tuple, ls: &Schema, r: &Tuple, rs: &Schema) -> Result<Value>;
    fn children(&self) -> &[ExprRef];        // ExprRef = Arc<dyn Expression>
    /* return_type, to_string, clone_with_children, as_any */
}
tuple.get_value(schema, col_idx)              // Value (module 3b)
self.val.clone()                              // Value is Clone: hand out a copy
if self.tuple_idx == 0 { left } else { right }
```

## Notes

**Why the schema travels with the tuple.** A `Tuple` is bytes; only a `Schema` says where column 2 starts. So `evaluate` takes both. The same expression, `#0.2`, works for any row of any table whose third column is what the planner expected; the planner (given) chose `2` after looking up the column's name in the child operator's output schema.

**`#0.2` is a position, not a name.** By the time an expression exists, names are gone: `ColumnValueExpression(tuple_idx, col_idx)` is "column `col_idx` of input `tuple_idx`". Inputs are numbered because joins have two: `#0.1 = #1.0` joins column 1 of the left input with column 0 of the right. Everything else has one input, tuple index 0. The optimizer (module 3h) rewrites these numbers when it moves a filter into a join.

**`Arc<dyn Expression>`.** Operators hold their expressions as shared trait objects, as BusTub holds `shared_ptr<AbstractExpression>`. Sharing is the point: the optimizer builds new plans out of parts of old ones without copying whole trees.

## In BusTub

`constant_value_expression.h` (`auto Evaluate(const Tuple *tuple, const Schema &schema) const -> Value override { return val_; }`) and `column_value_expression.h` (`return tuple_idx_ == 0 ? left_tuple->GetValue(&left_schema, col_idx_) : right_tuple->GetValue(&right_schema, col_idx_);`). The expressions in BusTub's `abstract_expression.h` are "modeled as trees, i.e. every expression may have a variable number of children".

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `class AbstractExpression { virtual Value Evaluate(...) const = 0; }` | `trait Expression { fn evaluate(&self, ...) -> Result<Value>; }` |
| `std::shared_ptr<AbstractExpression>` | `Arc<dyn Expression>` (`ExprRef`) |
| `dynamic_cast<const ColumnValueExpression *>(expr.get())` | `expr.as_any().downcast_ref::<ColumnValueExpression>()` |
| `const Tuple *tuple` (may be `nullptr` for `VALUES`) | `&Tuple`; `Tuple::empty()` stands for "no row" |
| `uint32_t col_idx_` indexing a vector with no check | `get_value` indexes the schema; an out-of-range column is a bug (panic) |

**Port rule:** a C++ class hierarchy with virtual methods becomes a trait; `shared_ptr` of the base class becomes `Arc<dyn Trait>`; `dynamic_cast` becomes a downcast through `Any`.

## Learn more
- [Trait objects](https://doc.rust-lang.org/book/ch18-02-trait-objects.html) · [`Any`](https://doc.rust-lang.org/std/any/trait.Any.html) · [`Arc`](https://doc.rust-lang.org/std/sync/struct.Arc.html) · [Crafting Interpreters: evaluating expressions](https://craftinginterpreters.com/evaluating-expressions.html)

## Performance

Evaluating `#0.2` costs a schema lookup and a decode: for a fixed-size column an offset read, for a VARCHAR a follow-the-offset and a `String` allocation. A scan that evaluates an expression per row per column pays that for every row; this is why real engines evaluate expressions on whole columns at once (vectorised execution) and why BusTub's batches (stage 3e) exist.

**Measure it.** Build a `Tuple` of ten integer columns and evaluate `#0.9` a million times; then the same for a VARCHAR column. The difference is the allocation.

## Hints

### Tuple index vs column index

`tuple_idx` chooses *which tuple*, `col_idx` chooses *which column of that tuple's schema*. A bug that reads `col_idx` of the left tuple for a right-side column returns plausible-looking numbers; the join test uses two different schemas to catch it.

### `evaluate` takes one tuple, `evaluate_join` two

`ColumnValueExpression::evaluate` ignores `tuple_idx`: with one input there is nothing to choose. Only `evaluate_join` looks at it.

### Return a copy

`Value` owns its data (a string is a `String`), so `Ok(self.val.clone())` is right; there is nothing to borrow across the call.
