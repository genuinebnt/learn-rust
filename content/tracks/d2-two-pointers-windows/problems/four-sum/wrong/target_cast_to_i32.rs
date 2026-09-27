pub fn four_sum(nums: &[i32], target: i64) -> Vec<[i32; 4]> {
    let mut v = nums.to_vec();
    v.sort_unstable();
    let n = v.len();
    let target = target as i32 as i64;
    let mut out = Vec::new();
    for a in 0..n {
        if a > 0 && v[a] == v[a - 1] {
            continue;
        }
        for b in a + 1..n {
            if b > a + 1 && v[b] == v[b - 1] {
                continue;
            }
            let (mut l, mut r) = (b + 1, n);
            while l + 1 < r {
                let sum = v[a] as i64 + v[b] as i64 + v[l] as i64 + v[r - 1] as i64;
                if sum < target {
                    l += 1;
                } else if sum > target {
                    r -= 1;
                } else {
                    out.push([v[a], v[b], v[l], v[r - 1]]);
                    l += 1;
                    while l + 1 < r && v[l] == v[l - 1] {
                        l += 1;
                    }
                    r -= 1;
                }
            }
        }
    }
    out
}
