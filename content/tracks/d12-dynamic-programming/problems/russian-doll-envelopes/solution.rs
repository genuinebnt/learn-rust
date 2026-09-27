pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
    let mut env = envelopes.to_vec();
    // Width ascending; equal widths by height descending, so two of the same width
    // can never both appear in the increasing run of heights.
    env.sort_unstable_by(|a, b| a.0.cmp(&b.0).then(b.1.cmp(&a.1)));
    let mut tails: Vec<u32> = Vec::new();
    for &(_, h) in &env {
        let k = tails.partition_point(|&t| t < h);
        if k == tails.len() {
            tails.push(h);
        } else {
            tails[k] = h;
        }
    }
    tails.len()
}
