With `extract_equi_join_keys` you can write the **rule**: find nested loop joins whose condition is equi-join keys and replace them with hash joins. The planner builds `a, b where a.x = b.y` as a cross join under a filter; the given rule `merge filter into NLJ` puts the filter into the join as its predicate; your rule then turns that join into a `HashJoin`. This is the optimization that makes joins of big tables feasible.

## The task

In `src/optimizer/optimizer.rs`, `optimize_nlj_as_hash_join(&self, plan: &PlanRef) -> PlanRef`:
- optimize the children first (`self.optimize_children(plan, &Self::optimize_nlj_as_hash_join)` gives the node with rewritten children);
- if the node is a `NestedLoopJoin` of type **Inner** or **Left** whose predicate gives equi-join keys, return a `HashJoin` plan with the same output schema, the same children, the same join type and those keys (`PlanNode::new(schema, children, PlanKind::HashJoin { left_key_expressions, right_key_expressions, join_type })`);
- otherwise return the node unchanged.

## Tests

- `inner join ... on a.x = b.p` shows `HashJoin { type=Inner, left_key=[#0.0], right_key=[#0.0] }` in `explain (o)` and no `NestedLoopJoin`.
- `from a, b where a.x = b.p` also becomes a hash join, with no `Filter` left.
- Several conditions become several keys; a condition that is not an equality (`<`, an extra `a.y > 5`, an `OR`, `a.x + 1 = b.p`) keeps the nested loop.
- Left joins become `HashJoin { type=Left`.
- The results equal the nested loop join's (the starter rules have none) for inner, left, cross-with-where, multi-key and swapped conditions.
- A three-way join becomes two hash joins, in both shapes `(a join b) join c` and `c join (a join b)`.

## Syntax and methods

```rust
let optimized = self.optimize_children(plan, &Self::optimize_nlj_as_hash_join);
if let PlanKind::NestedLoopJoin { predicate, join_type } = &optimized.kind { .. }
matches!(join_type, JoinType::Inner | JoinType::Left)
PlanNode::new(optimized.output_schema.clone(), optimized.children.clone(), PlanKind::HashJoin { .. })
```

## Notes

**Children first.** The rule is recursive: a three-way join has a join under a join. Rewriting the children first means that when the outer join is examined, its inputs are already hash joins (or not), and a rule that only looks at one node still optimizes the whole tree.

**Which pipeline runs it.** Unless `set force_optimizer_starter_rule=yes`, `Optimizer::optimize` applies: merge projection, merge filter into NLJ, **NLJ as hash join**, order-by as index scan, **sort+limit as top-N**, merge filter into scan, **seq scan as index scan**. Your three rules sit between the given ones; with the starter flag on, BusTub's own pipeline (which has the nested *index* join instead) runs, and that is what stage 3f's tests use.

**Equivalence.** The rewritten plan must return the same rows. The test compares each query's result under your pipeline with the result under the starter pipeline (which has no hash join). A rule that is wrong about NULL keys or duplicate matches shows up there.

**Right and full joins.** The hash join executor refuses them (module 3f), so the rule must not produce them: Inner and Left only.

## In BusTub

`nlj_as_hash_join.cpp` is a stub: `auto Optimizer::OptimizeNLJAsHashJoin(const AbstractPlanNodeRef &plan) -> AbstractPlanNodeRef { return plan; }`. `optimizer_custom_rules.cpp` lists the order: `OptimizeMergeProjection`, `OptimizeMergeFilterNLJ`, `OptimizeNLJAsHashJoin`, `OptimizeOrderByAsIndexScan`, `OptimizeSortLimitAsTopN`, `OptimizeMergeFilterScan`, `OptimizeSeqScanAsIndexScan`.

## The C/C++ way

| C / C++ | Rust |
|---|---|
| `std::vector<AbstractPlanNodeRef> children; for (child : plan->GetChildren()) children.emplace_back(Optimize...(child)); auto optimized = plan->CloneWithChildren(children);` | `self.optimize_children(plan, &Self::rule)` (given) |
| `std::make_shared<HashJoinPlanNode>(schema, left, right, left_keys, right_keys, type)` | `PlanNode::new(schema, vec![left, right], PlanKind::HashJoin {..})` |
| `return plan;` (the stub) | `optimized` |
| `dynamic_cast<const NestedLoopJoinPlanNode &>(*plan)` after a type check | `if let PlanKind::NestedLoopJoin { .. } = &optimized.kind` |

**Port rule:** a plan-node class hierarchy with `GetType()` and casts is an enum and `if let`.

## Learn more
- [`if let`](https://doc.rust-lang.org/book/ch06-03-if-let.html) · PostgreSQL [Hash Join in EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html) · DataFusion [optimizer rules](https://datafusion.apache.org/library-user-guide/query-optimizer.html)

## Performance

For two tables of 10,000 rows an equality join does 100 million comparisons as a nested loop and about 20,000 hash operations as a hash join: the difference between minutes and milliseconds. The tests of `p3.14` and `p3.15` join tables of hundreds of rows many times and are only fast with this rule.

**Measure it.** Join two 5,000-row tables on an equality under the starter pipeline (nested loop) and the default one (hash join) and compare.

## Hints

### Rewrite the node you rebuilt, not the original

`optimized` has the rewritten children; `plan` does not. Build the `HashJoin` from `optimized`'s children, or the rewrites of the subtree are lost.

### Keep the schema and the join type

The parent's expressions refer to the join's output by position; the hash join outputs left columns then right columns like the nested loop, so reuse `output_schema` as it is. A LEFT join must stay LEFT.

### No keys, no change

When `extract_equi_join_keys` returns `None`, return `optimized` untouched: a join with an `OR`, a range condition or a constant stays a nested loop.
