pub fn character_replacement(s: &str, k: usize) -> usize {
    let b = s.as_bytes();
    let (mut run, mut best) = (0, 0);
    for i in 0..b.len() {
        run = if i > 0 && b[i] == b[i - 1] { run + 1 } else { 1 };
        best = best.max(run);
    }
    (best + k).min(b.len())
}
