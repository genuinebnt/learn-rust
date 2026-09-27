pub fn num_squares(n: u32) -> u32 {
    let n = n as usize;
    // fewest[i] = the fewest squares that sum to i; 1 is a square, so every i is reachable.
    let mut fewest = vec![u32::MAX; n + 1];
    fewest[0] = 0;
    for i in 1..=n {
        let mut j = 1;
        while j * j <= i {
            fewest[i] = fewest[i].min(fewest[i - j * j] + 1);
            j += 1;
        }
    }
    fewest[n]
}
