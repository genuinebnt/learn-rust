pub fn dedup_sorted(v: &mut [i32]) -> usize {
    if v.is_empty() {
        return 0;
    }
    1 + v.windows(2).filter(|w| w[0] != w[1]).count()
}
