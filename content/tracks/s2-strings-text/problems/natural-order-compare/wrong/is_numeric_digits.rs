use std::cmp::Ordering;

/// Splits `s` after its leading run of ASCII digits.
fn digits(s: &str) -> (&str, &str) {
    s.split_at(s.find(|c: char| !c.is_ascii_digit()).unwrap_or(s.len()))
}

/// Natural order: runs of ASCII digits compare by numeric value, everything else char by char.
/// Strings that tie compare as plain strings, so the order is total.
pub fn natural_cmp(a: &str, b: &str) -> Ordering {
    let (mut x, mut y) = (a, b);
    loop {
        match (x.chars().next(), y.chars().next()) {
            (None, None) => return a.cmp(b),
            (None, Some(_)) => return Ordering::Less,
            (Some(_), None) => return Ordering::Greater,
            (Some(c), Some(d)) if c.is_ascii_digit() && d.is_ascii_digit() => {
                let ((nx, rx), (ny, ry)) = (digits(x), digits(y));
                let (nx, ny) = (nx.trim_start_matches('0'), ny.trim_start_matches('0'));
                let ord = nx.len().cmp(&ny.len()).then_with(|| nx.cmp(ny));
                if ord != Ordering::Equal {
                    return ord;
                }
                (x, y) = (rx, ry);
            }
            (Some(c), Some(d)) => {
                if c != d {
                    return c.cmp(&d);
                }
                (x, y) = (&x[c.len_utf8()..], &y[d.len_utf8()..]);
            }
        }
    }
}

/// The Luhn check: spaces are ignored, anything else must be an ASCII digit, and there must be at
/// least two digits.
pub fn luhn_valid(s: &str) -> bool {
    let (mut sum, mut count) = (0, 0);
    for c in s.chars().rev().filter(|&c| c != ' ') {
        if !c.is_numeric() {
            return false;
        }
        let d = c as u32 - '0' as u32;
        sum += if count % 2 == 1 {
            if d * 2 > 9 { d * 2 - 9 } else { d * 2 }
        } else {
            d
        };
        count += 1;
    }
    count >= 2 && sum % 10 == 0
}
