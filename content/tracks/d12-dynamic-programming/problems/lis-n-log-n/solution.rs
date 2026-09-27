pub fn length_of_lis(nums: &[i32]) -> usize {
    // tails[k] = the smallest last value of any increasing subsequence of length k + 1.
    // It is strictly increasing, so it can be binary-searched.
    let mut tails: Vec<i32> = Vec::new();
    for &x in nums {
        let k = tails.partition_point(|&t| t < x);
        if k == tails.len() {
            tails.push(x);
        } else {
            tails[k] = x;
        }
    }
    tails.len()
}
