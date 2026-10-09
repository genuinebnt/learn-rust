//! Port of `src/optimizer/*.cpp`. The optimizer rewrites a plan into one that produces the same result faster: each *rule* is a
//! function from a plan to a plan that looks for a pattern (a filter on a nested loop join, a sort over a scan) and replaces it. Rules
//! work bottom-up: optimise the children, rebuild the node, then look at the node. Plans are never edited in place.
//!
//! The rules the course asks you to write are marked (they return their input until you do); the others are given.

use std::sync::Arc;

use crate::binder::bound_order_by::OrderByType;
use crate::catalog::catalog::Catalog;
use crate::common::exception::Result;
use crate::execution::expressions::abstract_expression::{ExprRef, Expression};
use crate::execution::expressions::column_value_expression::ColumnValueExpression;
use crate::execution::expressions::comparison_expression::{ComparisonExpression, ComparisonType};
use crate::execution::expressions::constant_value_expression::ConstantValueExpression;
use crate::execution::expressions::logic_expression::{LogicExpression, LogicType};
use crate::execution::plans::plan_node::*;

pub struct Optimizer<'c, 'a> {
    pub catalog: &'c Catalog<'a>,
    force_starter_rule: bool,
}

impl<'c, 'a> Optimizer<'c, 'a> {
    pub fn new(catalog: &'c Catalog<'a>, force_starter_rule: bool) -> Optimizer<'c, 'a> {
        Optimizer { catalog, force_starter_rule }
    }

    /// The rules to apply, in order. `set force_optimizer_starter_rule=yes` selects the rules BusTub gives you (a nested index join
    /// instead of a hash join, no top-N); otherwise the rules you write are used.
    pub fn optimize(&self, plan: &PlanRef) -> Result<PlanRef> {
        let mut p = plan.clone();
        if self.force_starter_rule {
            p = self.optimize_merge_projection(&p);
            p = self.optimize_merge_filter_nlj(&p);
            p = self.optimize_nlj_as_index_join(&p);
            p = self.optimize_order_by_as_index_scan(&p);
            p = self.optimize_merge_filter_scan(&p);
            p = self.optimize_seq_scan_as_index_scan(&p);
            return Ok(p);
        }
        p = self.optimize_merge_projection(&p);
        p = self.optimize_merge_filter_nlj(&p);
        p = self.optimize_nlj_as_hash_join(&p);
        p = self.optimize_order_by_as_index_scan(&p);
        p = self.optimize_sort_limit_as_top_n(&p);
        p = self.optimize_merge_filter_scan(&p);
        p = self.optimize_seq_scan_as_index_scan(&p);
        Ok(p)
    }

    /// The number of rows BusTub assumes a table has, from its name (`..._1m`, `..._100k`, ...). For choosing the order of a join.
    pub fn estimated_cardinality(table_name: &str) -> Option<usize> {
        [("_1m", 1_000_000), ("_100k", 100_000), ("_50k", 50_000), ("_10k", 10_000), ("_1k", 1_000), ("_100", 100)]
            .iter()
            .find(|(suffix, _)| table_name.ends_with(suffix))
            .map(|(_, n)| *n)
    }

    fn optimize_children(&self, plan: &PlanRef, rule: &dyn Fn(&Self, &PlanRef) -> PlanRef) -> PlanRef {
        let children: Vec<PlanRef> = plan.children.iter().map(|c| rule(self, c)).collect();
        plan.clone_with_children(children)
    }

    // ---- merge projection ---------------------------------------------------------------------------------------------------

    /// Merges a projection that does nothing but pass its child's columns through (what `SELECT *`, aggregation and renaming produce).
    pub fn optimize_merge_projection(&self, plan: &PlanRef) -> PlanRef {
        let optimized = self.optimize_children(plan, &Self::optimize_merge_projection);
        if let PlanKind::Projection { expressions } = &optimized.kind {
            assert_eq!(optimized.children.len(), 1, "Projection with multiple children?? That's weird!");
            let child = &optimized.children[0];
            let (child_cols, proj_cols) = (child.output_schema.columns(), optimized.output_schema.columns());
            if child_cols.len() == proj_cols.len() && child_cols.iter().zip(proj_cols).all(|(a, b)| a.type_id() == b.type_id()) {
                let identical = expressions.iter().enumerate().all(|(idx, e)| {
                    e.as_any().downcast_ref::<ColumnValueExpression>().is_some_and(|c| c.tuple_idx() == 0 && c.col_idx() as usize == idx)
                });
                if identical {
                    return child.with_schema(optimized.output_schema.clone());
                }
            }
        }
        optimized
    }

    // ---- merge filter into nested loop join ---------------------------------------------------------------------------------

    /// In `SELECT * FROM a, b WHERE a.x = b.y` the filter says `#0.x = #0.y`; in the join it must say `#0.x = #1.y`: work out which side
    /// each column belongs to.
    pub fn rewrite_expression_for_join(expr: &ExprRef, left_column_cnt: usize, right_column_cnt: usize) -> Result<ExprRef> {
        let children = expr.children().iter().map(|c| Self::rewrite_expression_for_join(c, left_column_cnt, right_column_cnt)).collect::<Result<Vec<_>>>()?;
        if let Some(cv) = expr.as_any().downcast_ref::<ColumnValueExpression>() {
            assert_eq!(cv.tuple_idx(), 0, "tuple_idx cannot be value other than 0 before this stage.");
            let col_idx = cv.col_idx() as usize;
            if col_idx < left_column_cnt {
                return Ok(Arc::new(ColumnValueExpression::new(0, cv.col_idx(), cv.return_type().clone())));
            }
            if col_idx < left_column_cnt + right_column_cnt {
                return Ok(Arc::new(ColumnValueExpression::new(1, (col_idx - left_column_cnt) as u32, cv.return_type().clone())));
            }
            return Err(crate::common::exception::Exception::new(crate::common::exception::ExceptionType::Invalid, "col_idx not in range"));
        }
        Ok(expr.clone_with_children(children))
    }

    /// Is the predicate the constant TRUE?
    pub fn is_predicate_true(expr: &ExprRef) -> bool {
        expr.as_any().downcast_ref::<ConstantValueExpression>().is_some_and(|c| c.val.as_bool() == Some(true))
    }

    /// The planner plans `FROM a, b WHERE ...` as a cross join (predicate TRUE) under a filter; put the filter into the join.
    pub fn optimize_merge_filter_nlj(&self, plan: &PlanRef) -> PlanRef {
        let optimized = self.optimize_children(plan, &Self::optimize_merge_filter_nlj);
        if let PlanKind::Filter { predicate } = &optimized.kind {
            let child = &optimized.children[0];
            if let PlanKind::NestedLoopJoin { predicate: join_predicate, join_type } = &child.kind {
                if Self::is_predicate_true(join_predicate) {
                    let (left, right) = (&child.children[0], &child.children[1]);
                    let rewritten = Self::rewrite_expression_for_join(predicate, left.output_schema.column_count() as usize, right.output_schema.column_count() as usize)
                        .expect("the filter's columns come from the join's inputs");
                    return PlanNode::new(
                        optimized.output_schema.clone(),
                        vec![left.clone(), right.clone()],
                        PlanKind::NestedLoopJoin { predicate: rewritten, join_type: *join_type },
                    );
                }
            }
        }
        optimized
    }

    // ---- merge filter into scan ---------------------------------------------------------------------------------------------

    /// A filter directly on a sequential scan becomes the scan's `filter_predicate`.
    pub fn optimize_merge_filter_scan(&self, plan: &PlanRef) -> PlanRef {
        let optimized = self.optimize_children(plan, &Self::optimize_merge_filter_scan);
        if let PlanKind::Filter { predicate } = &optimized.kind {
            let child = &optimized.children[0];
            if let PlanKind::SeqScan { table_oid, table_name, filter_predicate: None } = &child.kind {
                return PlanNode::new(
                    optimized.output_schema.clone(),
                    vec![],
                    PlanKind::SeqScan { table_oid: *table_oid, table_name: table_name.clone(), filter_predicate: Some(predicate.clone()) },
                );
            }
        }
        optimized
    }

    /// A filter whose predicate is always TRUE is dropped.
    pub fn optimize_eliminate_true_filter(&self, plan: &PlanRef) -> PlanRef {
        let optimized = self.optimize_children(plan, &Self::optimize_eliminate_true_filter);
        if let PlanKind::Filter { predicate } = &optimized.kind {
            if Self::is_predicate_true(predicate) {
                return optimized.children[0].clone();
            }
        }
        optimized
    }

    // ---- indexes ------------------------------------------------------------------------------------------------------------

    /// The index on exactly the column `index_key_idx` of `table_name`, if there is one: (its oid, its name).
    pub fn match_index(&self, table_name: &str, index_key_idx: u32) -> Option<(IndexOid, String)> {
        self.catalog
            .get_table_indexes(table_name)
            .iter()
            .find(|i| i.index.metadata().get_key_attrs() == [index_key_idx])
            .map(|i| (i.index_oid, i.name.clone()))
    }

    /// `a JOIN b ON a.x = b.y` where `b` is a scan with an index on `y` becomes a nested index join (probe the index for each `a`).
    pub fn optimize_nlj_as_index_join(&self, plan: &PlanRef) -> PlanRef {
        let optimized = self.optimize_children(plan, &Self::optimize_nlj_as_index_join);
        if let PlanKind::NestedLoopJoin { predicate, join_type } = &optimized.kind {
            assert_eq!(optimized.children.len(), 2, "NLJ should have exactly 2 children.");
            if let Some(cmp) = predicate.as_any().downcast_ref::<ComparisonExpression>() {
                if cmp.comp_type == ComparisonType::Equal {
                    let (l, r) = (cmp.children()[0].as_any().downcast_ref::<ColumnValueExpression>(), cmp.children()[1].as_any().downcast_ref::<ColumnValueExpression>());
                    if let (Some(left_expr), Some(right_expr)) = (l, r) {
                        let right_plan = &optimized.children[1];
                        if let PlanKind::SeqScan { table_oid, table_name, .. } = &right_plan.kind {
                            // (outer = the side that reads the left input, inner = the side that reads the right input)
                            let sides = if left_expr.tuple_idx() == 0 && right_expr.tuple_idx() == 1 {
                                Some((left_expr, right_expr))
                            } else if left_expr.tuple_idx() == 1 && right_expr.tuple_idx() == 0 {
                                Some((right_expr, left_expr))
                            } else {
                                None
                            };
                            if let Some((outer_expr, inner_expr)) = sides {
                                if let Some((index_oid, index_name)) = self.match_index(table_name, inner_expr.col_idx()) {
                                    let key: ExprRef = Arc::new(ColumnValueExpression::new(0, outer_expr.col_idx(), outer_expr.return_type().clone()));
                                    return PlanNode::new(
                                        optimized.output_schema.clone(),
                                        vec![optimized.children[0].clone()],
                                        PlanKind::NestedIndexJoin {
                                            key_predicate: key,
                                            inner_table_oid: *table_oid,
                                            index_oid,
                                            index_name,
                                            index_table_name: table_name.clone(),
                                            inner_table_schema: right_plan.output_schema.clone(),
                                            join_type: *join_type,
                                        },
                                    );
                                }
                            }
                        }
                    }
                }
            }
        }
        optimized
    }

    /// `ORDER BY` columns that an index on the same columns already delivers in order: a sort over a scan becomes an index scan.
    pub fn optimize_order_by_as_index_scan(&self, plan: &PlanRef) -> PlanRef {
        let optimized = self.optimize_children(plan, &Self::optimize_order_by_as_index_scan);
        if let PlanKind::Sort { order_bys } = &optimized.kind {
            let mut order_by_column_ids = vec![];
            for ob in order_bys {
                if ob.order_type != OrderByType::Asc && ob.order_type != OrderByType::Default {
                    return optimized;
                }
                match ob.expr.as_any().downcast_ref::<ColumnValueExpression>() {
                    Some(cv) => order_by_column_ids.push(cv.col_idx()),
                    None => return optimized,
                }
            }
            let child = &optimized.children[0];
            if let PlanKind::SeqScan { table_oid, .. } = &child.kind {
                let table_info = self.catalog.get_table_by_oid(*table_oid).expect("the plan names a table that exists");
                for index in self.catalog.get_table_indexes(&table_info.name) {
                    if order_by_column_ids == index.index.metadata().get_key_attrs() {
                        return PlanNode::new(
                            optimized.output_schema.clone(),
                            vec![],
                            PlanKind::IndexScan { table_oid: table_info.oid, index_oid: index.index_oid, filter_predicate: None, pred_keys: vec![] },
                        );
                    }
                }
            }
        }
        optimized
    }

    // ---- the rules you write ------------------------------------------------------------------------------------------------

    /// Splits a predicate into its conjuncts: `a AND (b AND c)` is `[a, b, c]`; anything else (an `OR`, a comparison) is one conjunct.
    pub fn conjuncts(expr: &ExprRef, out: &mut Vec<ExprRef>) {
        match expr.as_any().downcast_ref::<LogicExpression>() {
            Some(l) if l.logic_type == LogicType::And => {
                for c in expr.children() {
                    Self::conjuncts(c, out);
                }
            }
            _ => out.push(expr.clone()),
        }
    }

    /// If **every** conjunct of a join predicate is `left column = right column` (written either way round), the key expressions of the
    /// two sides, in the same order: `(left keys, right keys)`. Anything else (another operator, an `OR`, both columns on one side, a
    /// constant) makes it `None`: the join cannot be a hash join.
    pub fn extract_equi_join_keys(predicate: &ExprRef) -> Option<(Vec<ExprRef>, Vec<ExprRef>)> {
        None // 3h-01: split the predicate into conjuncts (Optimizer::conjuncts); each must be a ComparisonExpression of type Equal whose two children are ColumnValueExpressions, one reading tuple 0 (left) and the other tuple 1 (right); collect the left columns and the right columns (as ColumnValueExpression(0, col_idx, type)); None if any conjunct is anything else
    }

    /// Turns a nested loop join whose predicate is equalities between the two sides into a hash join.
    pub fn optimize_nlj_as_hash_join(&self, plan: &PlanRef) -> PlanRef {
        plan.clone() // 3h-02: optimize the children first (self.optimize_children(plan, &Self::optimize_nlj_as_hash_join)); then, for an INNER or LEFT NestedLoopJoin whose predicate gives equi-join keys, a HashJoin with the same schema, children and join type; otherwise the node unchanged
    }

    /// Turns `Limit(Sort(child))` into `TopN(child)`.
    pub fn optimize_sort_limit_as_top_n(&self, plan: &PlanRef) -> PlanRef {
        plan.clone() // 3h-03: optimize the children first; then a Limit whose child is a Sort becomes a TopN with the limit's output schema, the sort's order-bys, n = the limit, and the sort's children
    }

    /// If the predicate is `column = constant` (either way round) or an `OR` of such equalities on the **same** column: that column's
    /// index in the scan's output and the constant expressions, in order. Otherwise `None`.
    pub fn extract_point_lookup(predicate: &ExprRef) -> Option<(u32, Vec<ExprRef>)> {
        None // 3h-04: an Equal comparison between a ColumnValueExpression and a ConstantValueExpression (either order) gives (the column's index, [the constant]); an OR of two such lookups on the same column gives the same column and the keys of both, left first; anything else None
    }

    /// Turns a scan with a point-lookup predicate on an indexed column into an index scan.
    pub fn optimize_seq_scan_as_index_scan(&self, plan: &PlanRef) -> PlanRef {
        plan.clone() // 3h-05: optimize the children first; then a SeqScan with a filter predicate that is (or has an AND-conjunct that is) a point lookup on a column with an index (self.match_index(table_name, column)) becomes an IndexScan with the scan's schema, that index, the keys as pred_keys, and the WHOLE predicate as filter_predicate; otherwise unchanged
    }
}
