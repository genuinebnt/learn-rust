//! Reading an `EXPLAIN ANALYZE` back: which operator spent the time itself?

#[derive(Debug, Clone, PartialEq)]
pub struct OpTime {
    pub op: String,
    pub depth: usize,
    pub inclusive_ms: f64,
    pub exclusive_ms: f64,
}

pub fn exclusive_times(analysis: &str) -> Vec<OpTime> {
    todo!("3i-c5: parse each line (indent, text, time); exclusive = inclusive minus the inclusive of the direct children, at least 0")
}

/// The operator with the largest exclusive time (the first when equal), `None` when there are no operators.
pub fn slowest(analysis: &str) -> Option<String> {
    todo!("3i-c5: the operator with the largest exclusive time")
}
