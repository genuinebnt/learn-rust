//! DISTINCT over rows of nullable integers.

use std::collections::HashSet;

pub type Row = Vec<Option<i64>>;

pub fn distinct_rows(rows: &[Row]) -> Vec<Row> {
    todo!("3b-c5: keep the first of each distinct row, treating NULL as equal to NULL")
}

pub fn distinct_count(rows: &[Row]) -> usize {
    todo!("3b-c5: how many distinct rows")
}
