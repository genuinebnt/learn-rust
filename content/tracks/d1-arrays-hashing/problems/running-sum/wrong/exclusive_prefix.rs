pub fn running_sum(nums: &[i32]) -> Vec<i32> {
    let mut total = 0;
    nums.iter()
        .map(|&x| {
            let before = total;
            total += x;
            before
        })
        .collect()
}
