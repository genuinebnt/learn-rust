pub fn min_window<'a>(s: &'a str, t: &str) -> &'a str {
    let b = s.as_bytes();
    let mut need = [0i32; 128];
    for c in t.bytes() {
        need[c as usize] += 1;
    }
    let mut missing = t.len();
    let mut best: Option<(usize, usize)> = None;
    let mut start = 0;
    for end in 0..b.len() {
        let c = b[end] as usize;
        if need[c] > 0 {
            missing -= 1;
        }
        need[c] -= 1;
        while missing == 0 {
            if best.is_none_or(|(l, r)| end + 1 - start < r - l) {
                best = Some((start, end + 1));
            }
            let d = b[start] as usize;
            need[d] += 1;
            if need[d] > 0 {
                missing += 1;
            }
            start += 1;
        }
    }
    best.map_or("", |(l, r)| &s[l..r])
}
