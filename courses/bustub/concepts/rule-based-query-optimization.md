---
title: Rule-based query optimization: rewriting plans
summary: What an optimizer rule is (a pattern and a replacement), why rules work bottom-up on immutable plans, why a rule must keep the result the same, how order of rules matters, and how to test a rule with EXPLAIN.
minutes: 9
---
The planner produces a *correct* plan, built from the shapes in the SQL text; the optimizer turns it into a *faster* one with the same result. A **rule-based** optimizer does so with a list of **rewrite rules**: each looks for a small pattern in the plan tree and, where it matches, replaces it with a cheaper equivalent. No cost model is needed for rules that are always an improvement.

```text
Limit ← Sort ← Scan              TopN ← Scan             (a bounded heap instead of a full sort)
NestedLoopJoin(a.x = b.y)        HashJoin(a.x ; b.y)     (linear instead of quadratic)
Filter(x = 5) ← SeqScan          IndexScan(x = 5)        (a lookup instead of a scan)
```

## Anatomy of a rule

1. **Optimize the children first** (recursion), then rebuild this node with the new children.
2. **Match** the node and what is under it: `is this a Limit whose child is a Sort?`
3. **Check the preconditions**: the join predicate is only equalities between the two sides; the index covers exactly the column.
4. **Build the replacement** from parts of the old nodes (reusing the unchanged children and expressions) or **return the node unchanged**.

The bottom-up order matters: by the time a node is examined its children are already rewritten, so a rule can assume it sees the best versions of them, and rules compose: a `Filter` merged into a `SeqScan` (one rule) makes an `IndexScan` possible (a later rule).

## Plans are values

A plan node is immutable and shared (`Arc`). A rule never edits a node: it builds a new one (`plan.clone_with_children(new_children)` copies the node with other children). This is what lets a rule return "the same plan" cheaply, lets the planner keep the original for `EXPLAIN`, and means a bug cannot corrupt a plan another part of the system is holding.

## Equivalence is the only contract

A rule may do anything that keeps the **result** the same, including the order of rows when the query specifies one (and including NULL behaviour). Typical mistakes:

- hashing a join with a predicate that is *not* purely an equality (the hash join would ignore the rest of the condition);
- turning `sort + limit` into top-N and getting ties in a different order;
- using an index for `col = 5` when the index is on `(col, other)` (a different structure with different rows to find);
- losing a column's alias or type when rebuilding a node (the parent's expressions refer to **positions**).

## Order of rules

The list is ordered on purpose. `merge filter into join` must run before `join to hash join`, because only after the merge does the join carry the equality predicate. When two rules could apply to the same node, the earlier wins.

## Testing a rule

Two kinds of test: *does it fire?* (`EXPLAIN` shows `HashJoin`; the test runner's `+ensure:hash_join`) and *does it preserve the result?* (compare with the unoptimized plan, as the course's tests do with the nested loop join). A rule that never fires passes the second kind trivially; a rule that fires wrongly fails it.

## C++ comparison

| C / C++ | Rust |
|---|---|
| `AbstractPlanNodeRef OptimizeX(const AbstractPlanNodeRef &plan)` recursing over `plan->GetChildren()` | `fn optimize_x(&self, plan: &PlanRef) -> PlanRef` |
| `plan->CloneWithChildren(children)` | `plan.clone_with_children(children)` |
| `dynamic_cast<const SortPlanNode &>(*plan)` | `match &plan.kind { PlanKind::Sort { .. } => .. }` |
| `std::make_shared<HashJoinPlanNode>(...)` | `PlanNode::new(schema, children, PlanKind::HashJoin { .. })` |

## In real code

### Using it: a rule on a tiny plan tree

```rust test
use std::rc::Rc;

#[derive(Debug, Clone, PartialEq)]
enum Plan {
    Scan(&'static str),
    Sort(Rc<Plan>),
    Limit(usize, Rc<Plan>),
    TopN(usize, Rc<Plan>),
}

/// Limit(n, Sort(x)) => TopN(n, x). Bottom-up: optimize the child first.
fn sort_limit_as_topn(plan: &Rc<Plan>) -> Rc<Plan> {
    let rebuilt = match plan.as_ref() {
        Plan::Scan(_) => return plan.clone(),
        Plan::Sort(c) => Rc::new(Plan::Sort(sort_limit_as_topn(c))),
        Plan::Limit(n, c) => Rc::new(Plan::Limit(*n, sort_limit_as_topn(c))),
        Plan::TopN(n, c) => Rc::new(Plan::TopN(*n, sort_limit_as_topn(c))),
    };
    if let Plan::Limit(n, child) = rebuilt.as_ref() {
        if let Plan::Sort(inner) = child.as_ref() {
            return Rc::new(Plan::TopN(*n, inner.clone())); // the replacement reuses the unchanged inner plan
        }
    }
    rebuilt
}

#[test]
fn the_pattern_is_replaced() {
    let plan = Rc::new(Plan::Limit(3, Rc::new(Plan::Sort(Rc::new(Plan::Scan("t"))))));
    assert_eq!(*sort_limit_as_topn(&plan), Plan::TopN(3, Rc::new(Plan::Scan("t"))));
}

#[test]
fn other_shapes_are_left_alone_and_the_input_is_not_changed() {
    let sort_only = Rc::new(Plan::Sort(Rc::new(Plan::Scan("t"))));
    assert_eq!(sort_limit_as_topn(&sort_only), sort_only);
    let limit_scan = Rc::new(Plan::Limit(3, Rc::new(Plan::Scan("t"))));
    assert_eq!(sort_limit_as_topn(&limit_scan), limit_scan);
    let original = Rc::new(Plan::Limit(1, Rc::new(Plan::Sort(Rc::new(Plan::Scan("u"))))));
    let _ = sort_limit_as_topn(&original);
    assert_eq!(*original, Plan::Limit(1, Rc::new(Plan::Sort(Rc::new(Plan::Scan("u"))))), "the old plan is untouched");
}

#[test]
fn the_rule_applies_below_other_nodes() {
    let plan = Rc::new(Plan::Limit(10, Rc::new(Plan::Limit(2, Rc::new(Plan::Sort(Rc::new(Plan::Scan("t"))))))));
    assert_eq!(*sort_limit_as_topn(&plan), Plan::Limit(10, Rc::new(Plan::TopN(2, Rc::new(Plan::Scan("t"))))));
}
```

### In the exercises

- **3h-01 to 3h-02:** NLJ → hash join (the condition parser, then the rewrite).
- **3h-03:** sort + limit → top-N.
- **3h-04 to 3h-05:** seq scan with a point predicate → index scan.
- **Given rules** (module 3d): merge projection, merge filter into NLJ, merge filter into scan, order-by → index scan, NLJ → index join; they show the shape.

### Where it is used

- **PostgreSQL**: `pull_up_subqueries`, `push down quals`, constant folding: rule-like transformations before cost-based path selection.
- **Apache Calcite / DataFusion / Spark Catalyst**: collections of rules (`PushDownFilter`, `EliminateLimit`, ...) applied until no rule fires (fixpoint).
- **LLVM**: passes are rewrite rules over IR; the same discipline (preserve semantics, order matters).
- **Compilers' peephole optimisers**: pattern → replacement.
