pub fn at_most_n_given_digit_set(digits: &[u8], n: u64) -> u64 {
    // Grow numbers one digit at a time, keeping the ones still at most n.
    let mut count = 0;
    let mut layer: Vec<u64> = vec![0];
    while !layer.is_empty() {
        let mut next = Vec::new();
        for &x in &layer {
            for &d in digits {
                if let Some(y) = x.checked_mul(10).and_then(|y| y.checked_add(d as u64)) {
                    if y <= n {
                        count += 1;
                        next.push(y);
                    }
                }
            }
        }
        layer = next;
    }
    count
}
