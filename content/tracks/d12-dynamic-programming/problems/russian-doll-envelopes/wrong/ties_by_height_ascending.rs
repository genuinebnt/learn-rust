pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
    let mut env = envelopes.to_vec();
    env.sort_unstable();
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
