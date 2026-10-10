//! The number of partners of each row of the left side, through an outer join.

/// A row: a join key that may be NULL, and a payload.
pub type Row = (Option<i64>, i64);

/// For each left row, `(its payload, the number of right rows with an equal key)`, in the order of the left rows.
pub fn partner_counts(left: &[Row], right: &[Row]) -> Vec<(i64, usize)> {
    // the LEFT join: (index of the left row, payload of its partner or None for the padding)
    let mut joined: Vec<(usize, Option<i64>)> = Vec::new();
    for (i, (key, _)) in left.iter().enumerate() {
        let mut found = false;
        for (rk, rp) in right {
            if key.is_some() && key == rk {
                found = true;
                joined.push((i, Some(*rp)));
            }
        }
        if !found {
            joined.push((i, None));
        }
    }
    let mut counts = vec![0usize; left.len()];
    for (i, partner) in &joined {
        let _ = partner;
        counts[*i] += 1;
    }
    left.iter().zip(counts).map(|(&(_, payload), n)| (payload, n)).collect()
}
