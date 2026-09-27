/// The longer of `a` and `b`; `a` on a tie.
pub fn longest(a: &str, b: &str) -> &str {
    if b.len() > a.len() {
        b
    } else {
        a
    }
}
