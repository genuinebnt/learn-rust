//! ROW_NUMBER, RANK and DENSE_RANK over sorted keys.

pub fn row_number(keys: &[i64]) -> Vec<usize> {
    (1..=keys.len()).collect()
}

pub fn dense_rank(keys: &[i64]) -> Vec<usize> {
    let mut out = Vec::with_capacity(keys.len());
    let mut rank = 0;
    for (i, k) in keys.iter().enumerate() {
        if i == 0 || keys[i - 1] != *k {
            rank += 1;
        }
        out.push(rank);
    }
    out
}

pub fn rank(keys: &[i64]) -> Vec<usize> {
    let mut out = Vec::with_capacity(keys.len());
    let mut current = 0;
    for (i, k) in keys.iter().enumerate() {
        if i == 0 || keys[i - 1] != *k {
            current += 1;
        }
        out.push(current);
    }
    out
}
