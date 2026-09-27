pub fn three_sum_closest(nums: &[i32], target: i32) -> i32 {
    let v = nums;
    let mut best = v[0] + v[1] + v[2];
    for i in 0..v.len() - 2 {
        let (mut l, mut r) = (i + 1, v.len() - 1);
        while l < r {
            let sum = v[i] + v[l] + v[r];
            if sum.abs_diff(target) < best.abs_diff(target) {
                best = sum;
            }
            if sum < target {
                l += 1;
            } else if sum > target {
                r -= 1;
            } else {
                return sum;
            }
        }
    }
    best
}
