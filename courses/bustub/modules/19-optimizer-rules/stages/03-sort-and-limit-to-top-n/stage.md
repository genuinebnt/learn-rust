`order by a desc limit 10` is planned as a `Limit` over a `Sort`. A top-N executor (module 3g) does the same with a bounded heap, using memory for ten rows instead of the whole table. The rule is the smallest in the module: find a `Limit` directly on a `Sort` and replace the pair by a `TopN`.

## The task

In `src/optimizer/optimizer.rs`, `optimize_sort_limit_as_top_n(&self, plan: &PlanRef) -> PlanRef`:
- optimize the children first;
- if the node is a `Limit` whose child is a `Sort`, return a `TopN` plan with the **limit node's output schema**, the **sort's children** (the sort's input becomes the top-N's input), the sort's `order_bys`, and `n` equal to the limit;
- otherwise return the node unchanged.

## Tests

- `order by a desc limit 5` shows `TopN { n=5` and no `ExternalMergeSort` or `Limit`.
- `order by` alone stays a sort; `limit` alone stays a limit.
- The rows are the same as sorting everything and taking the first rows (ascending, descending, several keys, ties).
- `limit 0` and a limit larger than the table work.
- Two top-N rules in one query (`select * from (select ... order by a desc limit 5) order by a asc limit 3`), and a top-N subquery inside a join.

## Syntax and methods

```rust
if let PlanKind::Limit { limit } = &optimized.kind {
    let child = &optimized.children[0];
    if let PlanKind::Sort { order_bys } = &child.kind {
        return PlanNode::new(optimized.output_schema.clone(), child.children.clone(), PlanKind::TopN { order_bys: order_bys.clone(), n: *limit });
    }
}
```

## Notes

**Pattern of two nodes.** A rule can look as deep as it needs: the `Limit` node checks its child's kind. The replacement *skips* the sort (its children become the top-N's), so the plan gets shorter.

**Ties.** `Sort` is stable and `Limit` keeps the first `n`; the `TopN` of module 3g breaks ties by arrival order, so the result is identical. The test `ties_come_out_as_a_stable_sort...` pins it.

**A projection between them.** `select a from t order by a limit 3` plans as `Limit ← Sort ← Projection`, so the pattern matches. A projection *above* the limit (`select b from (select ... limit 3)`) does not interfere. If the order-by columns are not in the select list the planner refuses the query before the optimizer sees it.

**Why not always?** `TopN` is better whenever the limit is smaller than the input; for `limit 1000000` of a smaller table it is no worse. A cost-based optimizer would compare; this one has no statistics and always applies the rule.

## In BusTub

`sort_limit_as_topn.cpp`: `/** @brief optimize sort + limit as top N */ auto Optimizer::OptimizeSortLimitAsTopN(...) { return plan; }` and `p3.17-topn.slt`, whose queries carry `+ensure:topn` (and one `+ensure:topn*2`), which turns on the `TopNCheckExecutor` that asserts the heap never exceeds N.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::make_shared<TopNPlanNode>(limit_plan.output_schema_, sort_plan.GetChildPlan(), sort_plan.GetOrderBy(), limit_plan.GetLimit())` | `PlanNode::new(schema, child.children.clone(), PlanKind::TopN { order_bys, n })` |
| `optimized_plan->GetType() == PlanType::Limit && child->GetType() == PlanType::Sort` | `if let PlanKind::Limit {..}` + `if let PlanKind::Sort {..}` |
| `GetChildAt(0)` on the limit to reach the sort | `optimized.children[0]` |

**Port rule:** pattern-matching a two-node shape is two nested `if let`s.

## Learn more
- [PostgreSQL: top-N heapsort](https://www.postgresql.org/docs/current/using-explain.html) · [`Rc`/`Arc` and sharing subtrees](https://doc.rust-lang.org/std/sync/struct.Arc.html)

## Performance

`O(rows log n)` and `O(n)` memory against `O(rows log rows)` and `O(rows)` (or disk passes). For `limit 10` over a million rows that is a scan plus ten-element heap operations instead of a sort of a million tuples through the buffer pool.

**Measure it.** `order by a desc limit 10` over 100,000 rows with the rule (default pipeline) and without it (starter pipeline).

## Hints

### The new node's children are the sort's children

If you keep the sort as the child of the `TopN`, the plan sorts everything and then keeps a heap: correct, and exactly what the rule exists to avoid.

### Use the limit's schema

The `Limit` and `Sort` have the same output schema (a limit does not change columns), but take it from the node that is being replaced at the top, so the parent keeps seeing what it saw.

### Children first, again

`limit(sort(limit(sort(x))))` needs the inner pair rewritten before the outer pair is examined.
