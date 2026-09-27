pub fn median(a: &[i32], b: &[i32]) -> Option<f64> {
    let (a, b) = if a.len() <= b.len() { (a, b) } else { (b, a) };
    let (m, n) = (a.len(), b.len());
    if m + n == 0 {
        return None;
    }
    let half = (m + n + 1) / 2;
    // Take i elements from a and half - i from b for the left half; search for the right i.
    let (mut lo, mut hi) = (0, m);
    loop {
        let i = lo + (hi - lo) / 2;
        let j = half - i;
        // Widen to i64 so the out-of-range sentinels can't collide with real values.
        let a_left = if i == 0 { i64::MIN } else { i64::from(a[i - 1]) };
        let a_right = if i == m { i64::MAX } else { i64::from(a[i]) };
        let b_left = if j == 0 { i64::MIN } else { i64::from(b[j - 1]) };
        let b_right = if j == n { i64::MAX } else { i64::from(b[j]) };
        if a_left > b_right {
            hi = i - 1;
        } else if b_left > a_right {
            lo = i + 1;
        } else {
            let left = a_left.max(b_left);
            return Some(if (m + n) % 2 == 1 {
                left as f64
            } else {
                (left + a_right.min(b_right)) as f64 / 2.0
            });
        }
    }
}
