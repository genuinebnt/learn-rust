pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
    let i = v.partition_point(|&y| y < x);
    v.insert(i, x);
}

pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
    let start = v.partition_point(|&y| y < lo);
    let end = v.partition_point(|&y| y <= hi);
    end.saturating_sub(start)
}
