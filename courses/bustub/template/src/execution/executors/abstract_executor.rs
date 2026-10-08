//! Port of `src/include/execution/executors/abstract_executor.h`. BusTub's executors use the **iterator** (Volcano) model with
//! batches: `init` prepares, then `next` is called until it says there is nothing more; each call fills a batch of up to `batch_size`
//! tuples (and the rids they came from). A parent pulls from its children the same way. Given code.

use crate::catalog::schema::Schema;
use crate::common::exception::Result;
use crate::common::rid::Rid;
use crate::storage::table::tuple::Tuple;

/// The number of tuples an executor produces per call to `next`. BusTub's `BUSTUB_BATCH_SIZE`.
pub const BUSTUB_BATCH_SIZE: usize = 20;

pub trait Executor {
    /// Prepares to produce tuples from the start. Called once, and again whenever a parent wants the same output a second time.
    fn init(&mut self) -> Result<()>;

    /// Replaces the contents of `tuple_batch` and `rid_batch` with the next at-most-`batch_size` tuples (and the rids of their source
    /// rows). Returns `false` when there are no more tuples (the batches are then empty).
    fn next(&mut self, tuple_batch: &mut Vec<Tuple>, rid_batch: &mut Vec<Rid>, batch_size: usize) -> Result<bool>;

    /// The schema of the tuples this executor produces.
    fn output_schema(&self) -> &Schema;
}

/// A boxed executor. The lifetime is the executor context's: executors borrow the catalog.
pub type ExecutorBox<'e> = Box<dyn Executor + 'e>;
