//! DISTINCT over rows of nullable integers.

use std::collections::HashSet;

pub type Row = Vec<Option<i64>>;

pub fn distinct_rows(rows: &[Row]) -> Vec<Row> {
    // @begin 3b-c5
    let mut seen: HashSet<&Row> = HashSet::new();
    rows.iter().filter(|r| seen.insert(r)).cloned().collect()
    //~ todo!("3b-c5: keep the first of each distinct row, treating NULL as equal to NULL")
    // @end
}

pub fn distinct_count(rows: &[Row]) -> usize {
    // @begin 3b-c5
    rows.iter().collect::<HashSet<_>>().len()
    //~ todo!("3b-c5: how many distinct rows")
    // @end
}
