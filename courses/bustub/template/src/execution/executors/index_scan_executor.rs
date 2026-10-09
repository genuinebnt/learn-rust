//! Port of `index_scan_executor.cpp`: reads a table through one of its indexes. Without `pred_keys` it reads every row **in key order**
//! (what `ORDER BY` on the indexed column wants); with `pred_keys` it looks each key up (what `WHERE col = constant` wants). Rows that
//! are deleted, or that fail the plan's `filter_predicate`, are skipped.

use std::sync::Arc;

use super::abstract_executor::Executor;
use crate::catalog::catalog::{IndexInfo, TableInfo};
use crate::catalog::schema::Schema;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::execution::executor_context::ExecutorContext;
use crate::execution::expressions::abstract_expression::ExprRef;
use crate::execution::plans::plan_node::{PlanKind, PlanRef};
use crate::storage::table::tuple::Tuple;

pub struct IndexScanExecutor<'e> {
    plan: PlanRef,
    table_info: &'e TableInfo<'e>,
    index_info: Arc<IndexInfo<'e>>,
    filter_predicate: Option<ExprRef>,
    pred_keys: Vec<ExprRef>,
    /// The rids to visit, in the order to visit them; `cursor` is how many were visited.
    rids: Vec<Rid>,
    cursor: usize,
}

impl<'e> IndexScanExecutor<'e> {
    pub fn new(ctx: &'e ExecutorContext<'e>, plan: PlanRef) -> Result<IndexScanExecutor<'e>> {
        let PlanKind::IndexScan { table_oid, index_oid, filter_predicate, pred_keys } = &plan.kind else { unreachable!("an IndexScanExecutor needs an IndexScan plan") };
        let table_info = ctx.catalog.table_info(*table_oid).ok_or_else(|| Exception::new(ExceptionType::Execution, "the table of an index scan does not exist"))?;
        let index_info = ctx.catalog.get_index_by_oid(*index_oid).ok_or_else(|| Exception::new(ExceptionType::Execution, "the index of an index scan does not exist"))?;
        let (filter_predicate, pred_keys) = (filter_predicate.clone(), pred_keys.clone());
        Ok(IndexScanExecutor { plan, table_info, index_info, filter_predicate, pred_keys, rids: vec![], cursor: 0 })
    }

    /// The rids this scan visits: with `pred_keys`, the rid under each key (in the order of the keys); without, every rid of the index in
    /// key order.
    fn collect_rids(&self) -> Result<Vec<Rid>> {
        Ok(self.index_info.index.scan_all()) // 3e-08: with pred_keys: evaluate each key (a constant), make a one-column key tuple with the index's key schema and look it up (Index::scan_key)
    }
}

impl Executor for IndexScanExecutor<'_> {
    fn init(&mut self) -> Result<()> {
        todo!("3e-07: remember the rids to visit (collect_rids) and start at the first")
    }

    fn next(&mut self, tuple_batch: &mut Vec<Tuple>, rid_batch: &mut Vec<Rid>, batch_size: usize) -> Result<bool> {
        tuple_batch.clear();
        rid_batch.clear();
        todo!("3e-07: fill the batch from the rids: fetch each tuple from the heap (get_tuple), skip deleted ones and those for which the filter predicate (if any) is not TRUE; true if the batch is not empty")
    }

    fn output_schema(&self) -> &Schema {
        &self.plan.output_schema
    }
}
