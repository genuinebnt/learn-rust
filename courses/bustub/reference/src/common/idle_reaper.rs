//! Which sessions have been idle in a transaction for too long?

#[derive(Debug, Clone, PartialEq, Eq)]
pub struct SessionInfo {
    pub id: u64,
    pub in_txn: bool,
    pub last_active_ms: u64,
}

/// Ids to abort: a transaction open and idle for more than `timeout_ms`, longest idle first, ties by id.
pub fn expired(sessions: &[SessionInfo], now_ms: u64, timeout_ms: u64) -> Vec<u64> {
    // @begin 4e-c4
    let mut hits: Vec<(u64, u64)> = sessions
        .iter()
        .filter(|s| s.in_txn && now_ms.saturating_sub(s.last_active_ms) > timeout_ms)
        .map(|s| (now_ms.saturating_sub(s.last_active_ms), s.id))
        .collect();
    hits.sort_by(|a, b| b.0.cmp(&a.0).then(a.1.cmp(&b.1)));
    hits.into_iter().map(|(_, id)| id).collect()
    //~ todo!("4e-c4: sessions with a transaction idle for more than the timeout, longest first, ties by id")
    // @end
}

/// Milliseconds until the next session (with a transaction, not yet expired) becomes expired.
pub fn next_check_in(sessions: &[SessionInfo], now_ms: u64, timeout_ms: u64) -> Option<u64> {
    // @begin 4e-c4
    sessions
        .iter()
        .filter(|s| s.in_txn)
        .map(|s| now_ms.saturating_sub(s.last_active_ms))
        .filter(|idle| *idle <= timeout_ms)
        .map(|idle| timeout_ms - idle + 1)
        .min()
    //~ todo!("4e-c4: the smallest time until a transaction-holding session passes the timeout")
    // @end
}
