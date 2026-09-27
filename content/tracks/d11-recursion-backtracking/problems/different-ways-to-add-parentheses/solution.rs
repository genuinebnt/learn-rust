pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
    // The expression is nums[0] ops[0] nums[1] ... ops[k-1] nums[k].
    fn ways(nums: &[i64], ops: &[u8]) -> Vec<i64> {
        if ops.is_empty() {
            return vec![nums[0]];
        }
        let mut out = Vec::new();
        for i in 0..ops.len() {
            // ops[i] is applied last: everything to its left, then everything to its right.
            let left = ways(&nums[..=i], &ops[..i]);
            let right = ways(&nums[i + 1..], &ops[i + 1..]);
            for &a in &left {
                for &b in &right {
                    out.push(match ops[i] {
                        b'+' => a + b,
                        b'-' => a - b,
                        _ => a * b,
                    });
                }
            }
        }
        out
    }
    let (mut nums, mut ops, mut cur) = (Vec::new(), Vec::new(), 0i64);
    for b in expression.bytes() {
        if b.is_ascii_digit() {
            cur = cur * 10 + i64::from(b - b'0');
        } else {
            nums.push(cur);
            ops.push(b);
            cur = 0;
        }
    }
    nums.push(cur);
    ways(&nums, &ops)
}
