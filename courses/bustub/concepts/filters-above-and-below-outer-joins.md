---
title: Filters above and below outer joins
summary: Which parts of a WHERE clause the optimizer may move below an outer join, why moving the wrong one changes the answer, and how a filter that rejects NULLs turns an outer join into an inner one.
minutes: 10
---
The cheapest row is the one never read. That is the argument for **filter pushdown**: if a query joins two tables and keeps only the rows with `a.y > 15`, it is better to discard those rows while scanning `a` than to join first and discard afterwards. For an inner join this is always allowed. For an outer join it is allowed on one side and wrong on the other, and the reason is a good way to understand what an outer join *is*.

## The wrong move

Use `a(x, y)` and `b(x, z)` from the previous article and the query

    select a.x from a left join b on a.x = b.x where b.z is null

It asks for the rows of `a` that have no partner in `b`, the classic "anti join". Suppose the optimizer pushes `b.z is null` below the join, onto the scan of `b`. The scan now keeps only the rows of `b` whose `z` is NULL: probably none. The join is then a LEFT join with an empty right side, so *every* row of `a` is padded and returned. The correct answer was the rows that found no partner. The two disagree whenever `a` has a row that does have a partner.

The mistake is about *when* the NULLs appear. In the original query, `b.z` is NULL for padded rows, and those NULLs are created by the join; the filter looks at them afterwards. Pushed down, the filter looks at `b` before the join and never sees the padding.

## The rule

A conjunct of the filter (one of the parts joined by `AND`) may move below the join onto an input when removing rows from that input *before* the join gives the same final rows as removing them after.

- **Inner join:** either input. A pair survives or dies together with its rows; nothing is created by the join.
- **Left join:** the left input only. Removing a left row before the join removes exactly the output rows built from it. Removing a right row before the join would create new padded rows (the left rows that lost their partner), which the filter above would never have produced.
- **Right join:** the right input only, symmetric.
- **Full join:** neither.

A conjunct that mentions columns of both inputs (`a.y + b.z > 100`) cannot move at all; it stays above the join. Only whole conjuncts move, so the optimizer first splits `p AND q AND r` into its parts, which is why the rule is easiest to write with a function that lists the conjuncts of an expression and one that reports which columns an expression reads.

One piece of bookkeeping: below the join a conjunct that read the right input must refer to columns by their position *in that input*, but above it positions count the left input's columns first. When a conjunct moves onto the right input its column numbers shift down by the width of the left side.

## A filter that makes the join smaller

Now the other direction. Take `a LEFT JOIN b ... WHERE b.z > 250`. The padded rows have `b.z = NULL`, and `NULL > 250` is unknown, so the filter removes every padded row. What is left is exactly what an inner join would have produced. The query was written as an outer join but behaves as an inner join, and the optimizer may treat it as one: the inner join can be reordered with others, executed by a hash join, and have the filter pushed to *both* inputs.

The test is: **does the condition fail whenever every column of the padded side is NULL?** For comparisons, `LIKE`, arithmetic and `||` the answer is yes: a NULL operand makes the value NULL. `AND` rejects NULLs if either part does; `OR` only if both parts do; `x IS NOT NULL` rejects them; `x IS NULL` does not (it is *true* for a padded row), and neither does `COALESCE(b.z, 0) > 250`, whose answer for a padded row depends on the default. `NOT (b.z > 250)` is unknown for a padded row, so it does reject them, but an analysis that simply says "NOT: cannot tell" loses only an optimization. Being wrong here is the dangerous direction: calling a condition NULL-rejecting when it is not turns an outer join into an inner one and silently drops rows.

For a FULL join each side is judged separately: a filter that rejects NULLs of the right side turns it into a RIGHT join (the rows padded on the right are gone, and only the half that preserves the right side is left), one that rejects the left side's NULLs gives a LEFT join, and both together an inner join.

The order of the rules matters: simplify first, then push down. After a LEFT join has become inner, the conjunct on `b` can move onto `b`'s scan, which it could not before.

## How you would test it

Every statement here is a claim that two plans return the same rows, so the natural test is differential: run the query with the rules on and with only the starter rules on, over random tables with NULLs and duplicates, with every join kind and a set of conditions that includes the nasty ones (`IS NULL`, `OR`, `COALESCE`). Add a plan-shape check for each rule you expect to fire, so a rule that never fires does not pass by being absent.

## In real code

### Using it: the same filter above and below a LEFT join

```rust test
type Row = (i32, Option<i32>); // (key, payload); None is NULL

/// `left LEFT JOIN right ON key` -> rows of (left key, right payload), right payload None when padded.
fn left_join(left: &[Row], right: &[Row]) -> Vec<(i32, Option<i32>)> {
    let mut out = vec![];
    for l in left {
        let mut found = false;
        for r in right {
            if l.0 == r.0 {
                found = true;
                out.push((l.0, r.1));
            }
        }
        if !found {
            out.push((l.0, None));
        }
    }
    out
}

#[test]
fn pushing_is_null_below_a_left_join_changes_the_answer() {
    let a = [(1, Some(0)), (2, Some(0)), (3, Some(0))];
    let b = [(2, Some(7)), (3, Some(9))];
    // WHERE b.z IS NULL, applied after the join: the left rows with no partner (and partners whose payload is NULL)
    let above: Vec<_> = left_join(&a, &b).into_iter().filter(|r| r.1.is_none()).collect();
    assert_eq!(above, vec![(1, None)]);
    // the same filter pushed onto b's scan: no b row passes, so every a row is padded
    let b_filtered: Vec<Row> = b.iter().copied().filter(|r| r.1.is_none()).collect();
    let below = left_join(&a, &b_filtered);
    assert_eq!(below.len(), 3);
    assert_ne!(above, below);
}

#[test]
fn a_null_rejecting_filter_removes_every_padded_row() {
    let a = [(1, Some(0)), (2, Some(0)), (3, Some(0))];
    let b = [(2, Some(7)), (3, Some(9))];
    // `b.z > 7` rejects NULLs: above the join it removes every padded row, so an inner join would give the same rows
    let kept: Vec<_> = left_join(&a, &b).into_iter().filter(|r| matches!(r.1, Some(z) if z > 7)).collect();
    assert_eq!(kept, vec![(3, Some(9))]);
}
```

### In the exercises

- **3j-02:** `optimize_filter_pushdown`: which join types let which side take a conjunct (the first test above is why a LEFT join may not take a filter on `b`), and the renumbering of columns.
- **3j-03:** `rejects_nulls` and `simplified_join_type`: the second test is the justification for turning the join into an inner join.
- **3j-07:** the boss compares optimized and plain plans over random filters and join kinds.

### Where it is used

PostgreSQL's planner calls the NULL-rejection analysis `reduce_outer_joins`: a qual is *strict* for a relation if it cannot be true when that relation's columns are NULL, and strict quals above a join let the planner turn it into an inner join and reorder it. The restriction on which side may take a pushed-down qual is the "outer join delay" rule in the same planner. MySQL calls the rewrite "outer join simplification" (`simplify_joins`), and SQL Server and Oracle have an equivalent rule.
