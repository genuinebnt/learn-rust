pub fn max_envelopes(envelopes: &[(u32, u32)]) -> usize {
    let mut env = envelopes.to_vec();
    env.sort_unstable();
    let mut best = vec![1usize; env.len()];
    for i in 0..env.len() {
        for j in 0..i {
            if env[j].0 < env[i].0 && env[j].1 < env[i].1 {
                best[i] = best[i].max(best[j] + 1);
            }
        }
    }
    best.into_iter().max().unwrap_or(0)
}
