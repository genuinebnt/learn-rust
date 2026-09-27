pub fn open_lock(deadends: &[&str], target: &str) -> Option<u32> {
    // Wrong: ignores deadends except at the start and the target.
    if deadends.contains(&"0000") || deadends.contains(&target) {
        return None;
    }
    Some(target.bytes().map(|b| { let d = u32::from(b - b'0'); d.min(10 - d) }).sum())
}
