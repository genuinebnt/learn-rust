//! Which sessions have been idle in a transaction for too long?

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SessionInfo {
    pub id: u64,
    pub in_txn: bool,
    pub last_active_ms: u64,
}

/// Ids to abort: a transaction open and idle for more than `timeout_ms`, longest idle first, ties by id.
pub fn expired(sessions: &[SessionInfo], now_ms: u64, timeout_ms: u64) -> Vec<u64> {
    todo!("4e-c4: sessions with a transaction idle for more than the timeout, longest first, ties by id")
}

/// Milliseconds until the next session (with a transaction, not yet expired) becomes expired.
pub fn next_check_in(sessions: &[SessionInfo], now_ms: u64, timeout_ms: u64) -> Option<u64> {
    todo!("4e-c4: the smallest time until a transaction-holding session passes the timeout")
}
