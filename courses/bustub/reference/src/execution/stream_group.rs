//! Grouping rows that arrive sorted by key.

#[derive(Debug, PartialEq, Eq)]
pub struct NotSorted {
    pub at: usize,
}

/// `(key, sum, count)` per group.
pub fn stream_group_sums(rows: &[(i64, i64)]) -> Result<Vec<(i64, i64, usize)>, NotSorted> {
    // @begin 3f-c5
    let mut out: Vec<(i64, i64, usize)> = Vec::new();
    for (i, &(key, value)) in rows.iter().enumerate() {
        match out.last_mut() {
            Some(g) if g.0 == key => {
                g.1 = g.1.wrapping_add(value);
                g.2 += 1;
            }
            Some(g) if g.0 > key => return Err(NotSorted { at: i }),
            _ => out.push((key, value, 1)),
        }
    }
    Ok(out)
    //~ todo!("3f-c5: extend the current group while the key repeats; start a new one when it grows; refuse a key that shrinks")
    // @end
}
