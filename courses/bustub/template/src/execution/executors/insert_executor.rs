//! Port of `insert_executor.cpp`: inserts every tuple of its child into a table (and into the table's indexes) and then produces one
//! row: how many it inserted.

use std::sync::Arc;

use super::abstract_executor::{Executor, ExecutorBox, BUSTUB_BATCH_SIZE};
use crate::catalog::catalog::{IndexInfo, TableInfo};
use crate::catalog::schema::Schema;
use crate::common::exception::{Exception, ExceptionType, Result};
use crate::common::rid::Rid;
use crate::execution::executor_context::ExecutorContext;
use crate::execution::plans::plan_node::{PlanKind, PlanRef};
use crate::storage::table::tuple::{Tuple, TupleMeta};
use crate::types::value::Value;

pub struct InsertExecutor<'e> {
    plan: PlanRef,
    table_info: &'e TableInfo<'e>,
    indexes: Vec<Arc<IndexInfo<'e>>>,
    child: ExecutorBox<'e>,
    /// The count has been produced.
    done: bool,
}

impl<'e> InsertExecutor<'e> {
    pub fn new(ctx: &'e ExecutorContext<'e>, plan: PlanRef, child: ExecutorBox<'e>) -> Result<InsertExecutor<'e>> {
        let PlanKind::Insert { table_oid } = &plan.kind else { unreachable!("an InsertExecutor needs an Insert plan") };
        let table_info = ctx.catalog.table_info(*table_oid).ok_or_else(|| Exception::new(ExceptionType::Execution, "the table of an insert does not exist"))?;
        let indexes = ctx.catalog.get_table_indexes(&table_info.name);
        Ok(InsertExecutor { plan, table_info, indexes, child, done: false })
    }

    /// Adds the tuple stored at `rid` to every index of the table. A key that is already in an index is ignored (BusTub's indexes keep
    /// unique keys and the catalog "silently ignores the error").
    fn insert_into_indexes(&self, tuple: &Tuple, rid: Rid) {
        // 3e-04: for every index, the key of the tuple (Tuple::key_from_tuple with the table's schema, the index's key schema and its key attributes) maps to rid
    }
}

impl Executor for InsertExecutor<'_> {
    fn init(&mut self) -> Result<()> {
        todo!("3e-03: forget that the count was produced and initialise the child")
    }

    fn next(&mut self, tuple_batch: &mut Vec<Tuple>, rid_batch: &mut Vec<Rid>, _batch_size: usize) -> Result<bool> {
        tuple_batch.clear();
        rid_batch.clear();
        todo!("3e-03: once: pull every batch from the child, insert each tuple into the heap (a TupleMeta with ts 0 and is_deleted false), call insert_into_indexes with the new rid, count them; answer with one tuple holding the count; every later call returns false")
    }

    fn output_schema(&self) -> &Schema {
        &self.plan.output_schema
    }
}
