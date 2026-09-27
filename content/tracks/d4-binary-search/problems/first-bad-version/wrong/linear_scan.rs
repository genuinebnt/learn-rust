pub fn first_bad(n: u32, is_bad: impl Fn(u32) -> bool) -> Option<u32> {
    (1..=n).find(|&v| is_bad(v))
}
