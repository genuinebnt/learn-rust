//! Retrying a transaction that lost a conflict.

use crate::common::exception::{Exception, ExceptionType};

/// Is this error a conflict the client should answer by running the transaction again?
pub fn is_retryable(e: &Exception) -> bool {
    todo!("4e-c1: Execution errors about conflicts and refused commits only")
}

/// Milliseconds to wait before attempt `attempt + 1`.
pub fn backoff_ms(attempt: usize, seed: u64) -> u64 {
    todo!("4e-c1: min(2^(attempt-1), 64), then a jitter in [base/2, base] that depends only on (attempt, seed)")
}

/// Runs `f(1)`, `f(2)`, ... until it succeeds, fails with something that is not retryable, or `max_attempts` calls were made.
pub fn run_with_retry<T>(max_attempts: usize, mut f: impl FnMut(usize) -> Result<T, Exception>) -> Result<(T, usize), Exception> {
    let _ = (max_attempts, &mut f);
    todo!("4e-c1: call f with the attempt number; retry only retryable errors while attempts remain")
}
