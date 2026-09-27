pub fn can_partition(nums: &[u32]) -> bool {
    let total: u32 = nums.iter().sum();
    if total % 2 == 1 {
        return false;
    }
    let half = (total / 2) as usize;
    // reach[s] = some subset of the numbers so far sums to s.
    let mut reach = vec![false; half + 1];
    reach[0] = true;
    for &x in nums {
        let x = x as usize;
        for s in (x..=half).rev() {
            reach[s] = reach[s] || reach[s - x];
        }
    }
    reach[half]
}
