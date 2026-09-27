pub fn find_max_form(strs: &[&str], m: usize, n: usize) -> usize {
    let mut sorted = strs.to_vec();
    sorted.sort_by_key(|s| s.len());
    let (mut zeros_left, mut ones_left, mut count) = (m, n, 0);
    for s in sorted {
        let zeros = s.bytes().filter(|&b| b == b'0').count();
        let ones = s.len() - zeros;
        if zeros <= zeros_left && ones <= ones_left {
            zeros_left -= zeros;
            ones_left -= ones;
            count += 1;
        }
    }
    count
}
