pub fn length_of_lis(nums: &[i32]) -> usize {
    let mut tails: Vec<i32> = Vec::new();
    for &x in nums {
        let k = tails.partition_point(|&t| t <= x);
        if k == tails.len() {
            tails.push(x);
        } else {
            tails[k] = x;
        }
    }
    tails.len()
}
