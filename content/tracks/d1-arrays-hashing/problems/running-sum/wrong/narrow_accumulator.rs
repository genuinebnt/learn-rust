pub fn running_sum(nums: &[i32]) -> Vec<i32> {
    let mut total: i16 = 0;
    nums.iter()
        .map(|&x| {
            total = total.wrapping_add(x as i16);
            total as i32
        })
        .collect()
}
