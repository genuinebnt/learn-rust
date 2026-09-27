pub fn take_tail(v: &mut Vec<i32>, at: usize) -> Vec<i32> {
    let at = at.min(v.len());
    v.split_off(at)
}

pub fn replace_range(v: &mut Vec<i32>, start: usize, end: usize, with: &[i32]) -> Vec<i32> {
    v.splice(start..end, with.iter().copied()).collect()
}
