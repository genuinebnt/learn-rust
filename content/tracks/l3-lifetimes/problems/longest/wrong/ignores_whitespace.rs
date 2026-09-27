/// The longer of `a` and `b`; `a` on a tie.
pub fn longest<'a>(a: &'a str, b: &'a str) -> &'a str {
    if b.trim().len() > a.trim().len() {
        b
    } else {
        a
    }
}
