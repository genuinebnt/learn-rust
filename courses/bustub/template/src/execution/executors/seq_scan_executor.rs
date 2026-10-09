//! Port of `seq_scan_executor.cpp`: reads every row of a table, in the order they are stored, skipping the deleted ones and (when the
//! optimizer merged a filter into the scan) the rows that do not satisfy the plan's `filter_predicate`.

use super::abstract_executor::Executor;
use crate::catalog::catalog::TableInfo;
use crate::catalog::schema::Schema;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::execution::executor_context::ExecutorContext;
use crate::execution::expressions::abstract_expression::ExprRef;
use crate::execution::plans::plan_node::{PlanKind, PlanRef};
use crate::storage::table::table_iterator::TableIterator;
use crate::storage::table::tuple::Tuple;

pub struct SeqScanExecutor<'e> {
    plan: PlanRef,
    table_info: &'e TableInfo<'e>,
    filter_predicate: Option<ExprRef>,
    iter: Option<TableIterator<'e>>,
}

/// Does `tuple` pass the scan's filter predicate? No predicate keeps everything; otherwise only the rows for which the predicate is
/// TRUE (FALSE and NULL are dropped). `schema` is the layout of the scan's tuples.
fn passes_filter(filter: &Option<ExprRef>, schema: &Schema, tuple: &Tuple) -> Result<bool> {
    Ok(true) // 3e-02: evaluate the predicate on the tuple; keep the row only if the answer is TRUE
}

impl<'e> SeqScanExecutor<'e> {
    pub fn new(ctx: &'e ExecutorContext<'e>, plan: PlanRef) -> Result<SeqScanExecutor<'e>> {
        let PlanKind::SeqScan { table_oid, filter_predicate, .. } = &plan.kind else { unreachable!("a SeqScanExecutor needs a SeqScan plan") };
        let table_info = ctx.catalog.table_info(*table_oid).ok_or_else(|| Exception::new(ExceptionType::Execution, "the table of a scan does not exist"))?;
        let filter_predicate = filter_predicate.clone();
        Ok(SeqScanExecutor { plan, table_info, filter_predicate, iter: None })
    }
}

impl Executor for SeqScanExecutor<'_> {
    fn init(&mut self) -> Result<()> {
        todo!("3e-01: start a table iterator (module 3c: the one that stops where the table ended when the scan began)")
    }

    fn next(&mut self, tuple_batch: &mut Vec<Tuple>, rid_batch: &mut Vec<Rid>, batch_size: usize) -> Result<bool> {
        tuple_batch.clear();
        rid_batch.clear();
        todo!("3e-01: fill the batch from the iterator: skip deleted tuples, keep those for which passes_filter(..) is true, stop at batch_size or the end; true if the batch is not empty")
    }

    fn output_schema(&self) -> &Schema {
        &self.plan.output_schema
    }
}
