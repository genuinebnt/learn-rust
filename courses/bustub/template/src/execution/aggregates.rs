//! The standard aggregates over a nullable column.

pub fn count_star(values: &[Option<i64>]) -> usize {
    values.len()
}

pub fn count_col(values: &[Option<i64>]) -> usize {
    values.iter().flatten().count()
}

pub fn sum(values: &[Option<i64>]) -> Option<i64> {
    values.iter().flatten().copied().reduce(|a, b| a.wrapping_add(b))
}

pub fn avg(values: &[Option<i64>]) -> Option<f64> {
    let total = sum(values)?;
    Some(total as f64 / count_star(values) as f64)
}
