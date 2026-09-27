pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
    let mut done = vec![false; profits.len()];
    for _ in 0..k {
        let best = (0..profits.len()).filter(|&i| !done[i] && capital[i] <= w).max_by_key(|&i| profits[i]);
        let Some(i) = best else { break };
        done[i] = true;
        w += profits[i];
    }
    w
}
