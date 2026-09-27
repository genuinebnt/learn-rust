pub fn three_sum(nums: &[i32]) -> Vec<[i32; 3]> {
    let mut v = nums.to_vec();
    v.sort_unstable();
    let mut out = Vec::new();
    for i in 0..v.len() {
        if i > 0 && v[i] == v[i - 1] {
            continue;
        }
        let (mut l, mut r) = (i + 1, v.len());
        while l + 1 < r {
            let sum = v[i] + v[l] + v[r - 1];
            if sum < 0 {
                l += 1;
            } else if sum > 0 {
                r -= 1;
            } else {
                out.push([v[i], v[l], v[r - 1]]);
                l += 1;
                while l + 1 < r && v[l] == v[l - 1] {
                    l += 1;
                }
                r -= 1;
            }
        }
    }
    out
}
