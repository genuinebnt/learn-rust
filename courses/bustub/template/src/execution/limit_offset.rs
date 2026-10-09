//! LIMIT and OFFSET over a vector of rows.

pub fn limit_offset(rows: &[i64], limit: Option<usize>, offset: usize) -> Vec<i64> {
    let take = limit.filter(|&n| n > 0).unwrap_or(usize::MAX);
    rows.iter().skip(offset).take(take).copied().collect()
}
