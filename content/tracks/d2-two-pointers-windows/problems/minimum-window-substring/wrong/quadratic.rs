pub fn min_window<'a>(s: &'a str, t: &str) -> &'a str {
    let b = s.as_bytes();
    let mut need = [0i32; 128];
    for c in t.bytes() {
        need[c as usize] += 1;
    }
    let mut best: Option<(usize, usize)> = None;
    for start in 0..b.len() {
        let mut left = need;
        let mut missing = t.len();
        for end in start..b.len() {
            let c = b[end] as usize;
            if left[c] > 0 {
                missing -= 1;
            }
            left[c] -= 1;
            if missing == 0 {
                if best.is_none_or(|(l, r)| end + 1 - start < r - l) {
                    best = Some((start, end + 1));
                }
                break;
            }
        }
    }
    best.map_or("", |(l, r)| &s[l..r])
}
