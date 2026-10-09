You have built the nodes and the front of the pipeline; now the planner has to know when to *make* them. The binder (given) turns `lower(name)` into "a call of a function named `lower` with one argument"; the planner turns that into an expression node through a **function factory**. The factory is empty: every call is an error ("func call lower not supported in planner yet"). After this stage `select lower('ABC');` works end to end, from the text you now lex and parse to the value your nodes compute.

> [!CHECK] `select upper(day_of_week) from __mock_table_schedule` reaches the factory with the name `upper` and one argument: which expression is that argument by then, and what is its position and type? What should happen for `select upper(1)`, for `select upper('a', 'b')` and for `select shout('a')`: at which layer does each of the three errors belong?
> ||The argument is already a `ColumnValueExpression` `#0.0` with the column's type: the binder resolved the name and the planner looked it up in the child's output schema. `upper(1)` is a type error (the `StringExpression` constructor reports it, the factory passes it on); `upper('a', 'b')` is an arity error (only the factory knows how many arguments each name takes); `shout` is a name error (no such function). All three are reported before any row is read.||
>
> - Who lower-cases `UPPER` in `select UPPER('x')`?
> - What does `explain` print for the plan, and where do you see your expression?
> - Why is the factory a function from names to nodes and not a `match` inside `StringExpression`?

## The task

In `src/planner/planner.rs`, `Planner::get_func_call_from_factory(func_name, args) -> Result<ExprRef>`:

- `"lower"` and `"upper"` with exactly one argument build a `StringExpression` of that kind over the argument;
- any other function name is an error (`func call {name} not supported in planner yet`);
- the wrong number of arguments is an error;
- an argument that is not a VARCHAR is an error (the `StringExpression` constructor already says so; pass its error on).

(The binder lower-cases names: `UPPER(x)` arrives as `upper`.)

The tests: the factory builds working `lower` and `upper`, refuses other names, argument counts and non-string arguments; and end to end through SQL: `select lower('MiXeD')`, both functions in one select list, nested calls, upper-case function names, wrong calls are errors, and over a mock table `explain` shows `upper(#0.0)` over a `MockScan`.

## Your freedom

How you look up the function (a `match`, a table of constructors) and how you check the arity.

## The Rust toolbox

**`match` on a string slice.** `match func_name { "lower" => .., "upper" => .., _ => return Err(..) }`: string literals are patterns.

**`Vec::remove`.** `args.remove(0)` takes the single argument out of the vector by value (so you can wrap it in an `Arc` without cloning).

**`Arc::new` into a trait object.** `Ok(Arc::new(StringExpression::new(arg, kind)?))`: the coercion from `Arc<StringExpression>` to `Arc<dyn Expression>` (`ExprRef`) happens at the `Ok`.

**`explain`.** `explain (o) select ...` prints the plan with each expression's `to_string`: if the text is not what you expect, the tree is not what you built.

## If this is new

- [L4 Traits & dispatch](/t/l4-traits-dispatch): coercing `Arc<T>` to `Arc<dyn Trait>`.
- [S1 Option & Result](/t/s1-option-result): returning `Err` early, passing on a constructor's error with `?`.

## Tests

- The factory builds `lower` and `upper` and refuses other names and other argument counts; it refuses non-string arguments.
- End to end through SQL, with the lexer and parser you wrote: `select lower('MiXeD')`, both functions, nested calls and upper-case names.
- Wrong calls (`upper(1)`, `lower('a', 'b')`, an unknown function, `lower()`) are errors.
- Over a mock table: the function is planned over a column and shows in `explain`.

## Hints

### Where is the arity checked?

Before you build anything: `args.len() != 1` is an error naming the function and the count it got.

### The error you do not write

`upper(1)`: the constructor refuses an INTEGER argument with a type error. Pass it on with `?`; do not write a second check.

## Performance

The factory runs once per call site per query, at planning time; it never runs per row. A planner that looked functions up by string for every row would waste the work: resolve once, evaluate many times.

**Measure it.** Plan a query with a hundred calls of `lower` and time the planning; compare with evaluating the plan over a thousand rows.

## Experiment

Optional. Predict first, then run.

1. **A third function.** Add `length(x)` returning an INTEGER. Which three places change (a new expression type, the factory, `explain` text)?
2. **Case.** Make the factory case-sensitive and the binder not lower-case names: which tests catch the split of responsibility?

## Other designs

- **A match in the planner (ours, BusTub's).**
- **A function registry** (`HashMap<&str, fn(Vec<ExprRef>) -> Result<ExprRef>>`) filled at start-up, so extensions can add functions.
- **Overload resolution by argument types** (PostgreSQL): the same name picks different implementations.
- **Binding functions in the binder**, so the planner receives resolved functions.

## In BusTub

`Planner::GetFuncCallFromFactory` in `src/planner/plan_func_call.cpp`:

```cpp
if (func_name == "lower" || func_name == "upper") { ... return std::make_shared<StringExpression>(args[0], ...); }
throw Exception(fmt::format("func call {} not supported in planner yet", func_name));
```

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `if (func_name == "lower" \|\| func_name == "upper")` | `match func_name { "lower" => .., "upper" => .., _ => .. }` |
| `std::make_shared<StringExpression>(args[0], kind)` | `Arc::new(StringExpression::new(arg, kind)?)` |
| `throw Exception(...)` | `return Err(exception(..))` |

**Port rule:** a chain of string comparisons becomes a `match` on the string slice; `make_shared` becomes `Arc::new`.

## Learn more

- PostgreSQL's [`EXPLAIN`](https://www.postgresql.org/docs/current/sql-explain.html) · BusTub's [expression factory](https://github.com/cmu-db/bustub/blob/master/src/planner/plan_func_call.cpp)
