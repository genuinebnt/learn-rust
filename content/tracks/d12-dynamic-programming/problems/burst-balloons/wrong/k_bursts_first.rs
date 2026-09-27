pub fn max_coins(nums: &[u32]) -> u64 {
    let mut a: Vec<u64> = vec![1];
    a.extend(nums.iter().map(|&x| x as u64));
    a.push(1);
    let m = a.len();
    let mut best = vec![vec![0u64; m]; m];
    for len in 2..m {
        for i in 0..m - len {
            let j = i + len;
            best[i][j] = (i + 1..j).map(|k| best[i][k] + best[k][j] + a[k - 1] * a[k] * a[k + 1]).max().unwrap();
        }
    }
    best[0][m - 1]
}
