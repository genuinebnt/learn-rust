//! Port of `update_executor.cpp`: replaces every tuple its child produces by a new one made of the plan's `target_expressions`
//! (evaluated on the old tuple), and produces one row: how many it updated.
//!
//! The update is a **delete followed by an insert**: the old tuple is marked deleted and the new one is stored (a new rid, since the
//! new tuple may have another size), and the table's indexes follow.

use std::sync::Arc;

use super::abstract_executor::{Executor, ExecutorBox, BUSTUB_BATCH_SIZE};
use crate::catalog::catalog::{IndexInfo, TableInfo};
use crate::catalog::schema::Schema;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::execution::executor_context::ExecutorContext;
use crate::execution::expressions::abstract_expression::ExprRef;
use crate::execution::plans::plan_node::{PlanKind, PlanRef};
use crate::storage::table::tuple::{Tuple, TupleMeta};
use crate::types::value::Value;

pub struct UpdateExecutor<'e> {
    plan: PlanRef,
    table_info: &'e TableInfo<'e>,
    indexes: Vec<Arc<IndexInfo<'e>>>,
    target_expressions: Vec<ExprRef>,
    child: ExecutorBox<'e>,
    done: bool,
}

impl<'e> UpdateExecutor<'e> {
    pub fn new(ctx: &'e ExecutorContext<'e>, plan: PlanRef, child: ExecutorBox<'e>) -> Result<UpdateExecutor<'e>> {
        let PlanKind::Update { table_oid, target_expressions } = &plan.kind else { unreachable!("an UpdateExecutor needs an Update plan") };
        let table_info = ctx.catalog.table_info(*table_oid).ok_or_else(|| Exception::new(ExceptionType::Execution, "the table of an update does not exist"))?;
        let indexes = ctx.catalog.get_table_indexes(&table_info.name);
        let target_expressions = target_expressions.clone();
        Ok(UpdateExecutor { plan, table_info, indexes, target_expressions, child, done: false })
    }

    /// The new tuple for `old`: every target expression evaluated on the old tuple, laid out with the table's schema.
    fn make_new_tuple(&self, old: &Tuple) -> Result<Tuple> {
        todo!("3e-06: evaluate each target expression on the old tuple (with the child's output schema) and build a tuple of those values with the table's schema")
    }
}

impl Executor for UpdateExecutor<'_> {
    fn init(&mut self) -> Result<()> {
        todo!("3e-06: forget that the count was produced and initialise the child")
    }

    fn next(&mut self, tuple_batch: &mut Vec<Tuple>, rid_batch: &mut Vec<Rid>, _batch_size: usize) -> Result<bool> {
        tuple_batch.clear();
        rid_batch.clear();
        todo!("3e-06: once: for every tuple of the child build the new tuple (make_new_tuple), mark the old heap tuple deleted and delete its index entries, insert the new tuple into the heap and its index entries under the new rid, count; answer with one tuple holding the count; later calls return false")
    }

    fn output_schema(&self) -> &Schema {
        &self.plan.output_schema
    }
}
