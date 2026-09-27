pub fn min_add_to_make_valid(s: &str) -> usize {
    let open = s.bytes().filter(|&b| b == b'(').count();
    let close = s.len() - open;
    open.abs_diff(close)
}
