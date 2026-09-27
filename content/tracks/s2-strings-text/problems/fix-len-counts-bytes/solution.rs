/// Centers `s` in a field `width` characters wide, padding with `fill`.
/// Odd padding puts the extra character on the right.
pub fn center(s: &str, width: usize, fill: char) -> String {
    let len = s.chars().count();
    if len >= width {
        return s.to_string();
    }
    let left = (width - len) / 2;
    let right = width - len - left;
    let mut out = String::new();
    out.extend(std::iter::repeat(fill).take(left));
    out.push_str(s);
    out.extend(std::iter::repeat(fill).take(right));
    out
}
