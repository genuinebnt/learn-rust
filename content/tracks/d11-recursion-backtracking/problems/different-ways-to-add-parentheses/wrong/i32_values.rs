pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
    fn ways(nums: &[i32], ops: &[u8]) -> Vec<i32> {
        if ops.is_empty() {
            return vec![nums[0]];
        }
        let mut out = Vec::new();
        for i in 0..ops.len() {
            for &a in &ways(&nums[..=i], &ops[..i]) {
                for &b in &ways(&nums[i + 1..], &ops[i + 1..]) {
                    out.push(match ops[i] { b'+' => a + b, b'-' => a - b, _ => a * b });
                }
            }
        }
        out
    }
    let (mut nums, mut ops, mut cur) = (Vec::new(), Vec::new(), 0i32);
    for b in expression.bytes() {
        if b.is_ascii_digit() {
            cur = cur * 10 + i32::from(b - b'0');
        } else {
            nums.push(cur);
            ops.push(b);
            cur = 0;
        }
    }
    nums.push(cur);
    ways(&nums, &ops).into_iter().map(i64::from).collect()
}
