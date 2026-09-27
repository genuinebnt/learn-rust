pub fn insert_sorted(v: &mut Vec<i32>, x: i32) {
    let i = v.partition_point(|&y| y < x);
    v.insert(i, x);
}

pub fn count_in_range(v: &[i32], lo: i32, hi: i32) -> usize {
    v.iter().filter(|&&y| lo <= y && y <= hi).count()
}
