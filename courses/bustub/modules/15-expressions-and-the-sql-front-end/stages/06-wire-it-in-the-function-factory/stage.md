You have built the nodes; now the planner has to know when to *make* them. The binder (given) turns `lower(name)` into "a call of a function named `lower` with one argument"; the planner turns that into an expression node through a **function factory**. The factory is empty: every call is an error ("func call lower not supported in planner yet"). After this stage `select lower('ABC');` works end to end.

## The task

In `src/planner/planner.rs`, `Planner::get_func_call_from_factory(func_name, args) -> Result<ExprRef>`:
- `"lower"` and `"upper"` with exactly one argument build a `StringExpression` of that kind over the argument;
- any other function name is an error (`func call {name} not supported in planner yet`);
- the wrong number of arguments is an error;
- an argument that is not a VARCHAR is an error (the `StringExpression` constructor already says so; pass its error on).

(Names reach the factory lower-cased by the binder: `UPPER(x)` is `upper`.)

## Tests

- The factory builds working `lower` and `upper` expressions and refuses other names and other argument counts.
- It refuses non-string arguments.
- End to end through SQL: `select lower('MiXeD')`, both functions in one select list, nested calls, upper-case function names.
- Wrong calls (`upper(1)`, `lower('a', 'b')`, an unknown function, `lower()`) are errors.
- Over a table: the function is planned over a column of a mock table, and `explain` shows `upper(#0.0)` over a `MockScan`.

## Syntax and methods

```rust
match func_name {
    "lower" => StringExpressionType::Lower,
    _ => return Err(Exception::new(ExceptionType::Invalid, format!("..."))),
}
if args.len() != 1 { return Err(..) }
Ok(Arc::new(StringExpression::new(args.remove(0), kind)?))     // Vec::remove(0) moves the argument out
```

## Notes

**The pipeline, once.** `execute_sql` (given, `src/common/bustub_instance.rs`) runs: the **parser** turns text into a syntax tree; the **binder** turns names into catalog objects and column references into `[table, column]` paths, producing a "bound" tree; the **planner** turns that into a tree of plan nodes with expressions in them (this is where your factory is called); the **optimizer** rewrites the plan; the **engine** builds an executor per node and pulls tuples through them. `explain` prints the plan between the planner and the engine. Type `explain select ...;` in the shell and read it from the bottom: the leaf scans first, then what is computed over them.

**Names are resolved before the planner.** The planner sees `upper(__mock_table_schedule.day_of_week)` and turns the column reference into `#0.0` by looking at the *output schema of the child plan*: "the column called `__mock_table_schedule.day_of_week` is the 0th of the MockScan's output". That is why plan schemas carry qualified names.

**Why a factory, not a `match` at the call site.** One table, one place, so a new function is a one-line change: BusTub's `GetBinaryExpressionFromFactory` (given) maps `=`, `<`, `+`, `and`, ... the same way, and `GetFuncCallFromFactory` is the one left for you.

## In BusTub

`src/planner/plan_func_call.cpp` (`auto Planner::GetFuncCallFromFactory(const std::string &func_name, std::vector<AbstractExpressionRef> args) -> AbstractExpressionRef { throw Exception(fmt::format("func call {} not supported in planner yet", func_name)); }`), `expression_factory.cpp` (`GetBinaryExpressionFromFactory`), and `planner.cpp` (`PlanQuery`).

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (func_name == "lower") { return std::make_shared<StringExpression>(args[0], StringExpressionType::Lower); }` | `match func_name { "lower" => .., "upper" => .., _ => return Err(..) }` |
| `args[0]` with no bounds check (UB for `lower()`) | check `args.len()`, then `args.remove(0)` moves the value out |
| `throw Exception(...)` caught by the SQL driver | `Err(Exception)` returned up to `execute_sql` |
| `std::make_shared<T>(...)` converted to `shared_ptr<Base>` | `Arc::new(T)` coerced to `Arc<dyn Expression>` |

**Port rule:** an unchecked `args[i]` in C++ is a length check and an error in Rust; a function table is a `match` on the name.

## Learn more
- [`Vec::remove`](https://doc.rust-lang.org/std/vec/struct.Vec.html#method.remove) · [PostgreSQL: EXPLAIN](https://www.postgresql.org/docs/current/sql-explain.html) · [BusTub's planner](https://github.com/cmu-db/bustub/blob/master/src/planner/planner.cpp)

## Performance

The factory runs once per query, at plan time, so it costs nothing per row. What matters is what it builds: a tree whose depth is the number of nested function calls, each evaluated once per row.

**Measure it.** Time `select lower(upper(lower(upper(github_id)))) from __mock_table_tas_2022` repeated 10,000 times (use `generate_mock_table`) against `select github_id`, to see the per-row cost of four string nodes.

## Hints

### Check the count before indexing

`args[0]` on an empty vector panics, and `lower()` is a test. Check `args.len() != 1` first.

### `?` does the type check

`StringExpression::new(arg, kind)?` already returns the error for a non-string argument. Do not write a second check.

### `explain` is your debugger

If the result is wrong, `explain` the same query in the shell (`cargo run --bin bustub_shell`): the plan shows the expression the factory built (`upper(#0.0)`), which tells you whether the factory or the evaluation is at fault.
