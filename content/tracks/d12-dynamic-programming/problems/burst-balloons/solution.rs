pub fn max_coins(nums: &[u32]) -> u64 {
    // Sentinel 1s at both ends: a balloon at the edge multiplies by 1.
    let mut a: Vec<u64> = Vec::with_capacity(nums.len() + 2);
    a.push(1);
    a.extend(nums.iter().map(|&x| x as u64));
    a.push(1);
    let m = a.len();
    // best[i][j] = the most coins from bursting every balloon strictly between i and j.
    // If k is the LAST one burst there, its neighbours at that moment are i and j.
    let mut best = vec![vec![0u64; m]; m];
    for len in 2..m {
        for i in 0..m - len {
            let j = i + len;
            best[i][j] = (i + 1..j).map(|k| best[i][k] + best[k][j] + a[i] * a[k] * a[j]).max().unwrap();
        }
    }
    best[0][m - 1]
}
