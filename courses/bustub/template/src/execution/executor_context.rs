//! Port of `src/include/execution/executor_context.h`: what an executor may use while it runs: the catalog, the buffer pool and the
//! options of this execution. Given code.

use std::sync::atomic::AtomicUsize;
use std::sync::{Arc, Mutex};

use super::check_options::CheckOptions;
use crate::buffer::buffer_pool_manager::BufferPoolManager;
use crate::catalog::catalog::Catalog;
use crate::concurrency::transaction::Transaction;
use crate::concurrency::transaction_manager::TransactionManager;

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
    /// The transaction the statement runs in (module 4); `None` runs it without versions, as modules 3e to 3h do.
    txn: Option<Arc<Transaction>>,
    txn_mgr: Option<&'e TransactionManager>,
}

impl<'e> ExecutorContext<'e> {
    pub fn new(catalog: &'e Catalog<'e>, bpm: &'e BufferPoolManager, is_delete: bool) -> ExecutorContext<'e> {
        ExecutorContext { catalog, bpm, nlj_check_exec_set: Mutex::new(vec![]), check_options: CheckOptions::default(), is_delete, txn: None, txn_mgr: None }
    }

    pub fn with_check_options(mut self, check_options: CheckOptions) -> ExecutorContext<'e> {
        self.check_options = check_options;
        self
    }

    /// Runs the statement inside `txn`, whose versions `txn_mgr` keeps.
    pub fn with_txn(mut self, txn: Arc<Transaction>, txn_mgr: &'e TransactionManager) -> ExecutorContext<'e> {
        self.txn = Some(txn);
        self.txn_mgr = Some(txn_mgr);
        self
    }

    pub fn txn(&self) -> Option<&Arc<Transaction>> {
        self.txn.as_ref()
    }

    pub fn txn_mgr(&self) -> Option<&'e TransactionManager> {
        self.txn_mgr
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
