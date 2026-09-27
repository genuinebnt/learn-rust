pub fn min_cost(n: u32, cuts: &[u32]) -> u64 {
    let mut pts: Vec<u64> = Vec::with_capacity(cuts.len() + 2);
    pts.push(0);
    pts.extend(cuts.iter().map(|&c| c as u64));
    pts.push(n as u64);
    pts.sort_unstable();
    let m = pts.len();
    // cost[i][j] = the cheapest way to make every cut strictly between pts[i] and pts[j].
    let mut cost = vec![vec![0u64; m]; m];
    for len in 2..m {
        for i in 0..m - len {
            let j = i + len;
            // Whichever cut k goes first costs the whole piece, then splits it in two.
            let best = (i + 1..j).map(|k| cost[i][k] + cost[k][j]).min().unwrap();
            cost[i][j] = pts[j] - pts[i] + best;
        }
    }
    cost[0][m - 1]
}
