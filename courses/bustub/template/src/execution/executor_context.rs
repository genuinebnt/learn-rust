//! Port of `src/include/execution/executor_context.h`: what an executor may use while it runs: the catalog, the buffer pool and the
//! options of this execution. Given code.

use std::sync::atomic::AtomicUsize;
use std::sync::{Arc, Mutex};

use super::check_options::CheckOptions;
use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::catalog::catalog::Catalog;

/// How many times an executor was initialised and how many batches it produced; the nested loop join check compares two of them.
#[derive(Debug, Default)]
pub struct InitCheckCounters {
    pub n_init: AtomicUsize,
    pub n_next: AtomicUsize,
}

pub struct ExecutorContext<'e> {
    pub catalog: &'e Catalog<'e>,
    pub bpm: &'e BufferPoolManager,
    /// Pairs (left, right) of counters of the nested loop joins checked by `+ensure:nlj_init_check`.
    nlj_check_exec_set: Mutex<Vec<(Arc<InitCheckCounters>, Arc<InitCheckCounters>)>>,
    check_options: CheckOptions,
    is_delete: bool,
}

impl<'e> ExecutorContext<'e> {
    pub fn new(catalog: &'e Catalog<'e>, bpm: &'e BufferPoolManager, is_delete: bool) -> ExecutorContext<'e> {
        ExecutorContext { catalog, bpm, nlj_check_exec_set: Mutex::new(vec![]), check_options: CheckOptions::default(), is_delete }
    }

    pub fn with_check_options(mut self, check_options: CheckOptions) -> ExecutorContext<'e> {
        self.check_options = check_options;
        self
    }

    pub fn check_options(&self) -> &CheckOptions {
        &self.check_options
    }

    pub fn add_check_executor(&self, left: Arc<InitCheckCounters>, right: Arc<InitCheckCounters>) {
        self.nlj_check_exec_set.lock().unwrap().push((left, right));
    }

    pub fn nlj_check_exec_set(&self) -> Vec<(Arc<InitCheckCounters>, Arc<InitCheckCounters>)> {
        self.nlj_check_exec_set.lock().unwrap().clone()
    }

    /// Is this a DELETE or UPDATE statement?
    pub fn is_delete(&self) -> bool {
        self.is_delete
    }
}
