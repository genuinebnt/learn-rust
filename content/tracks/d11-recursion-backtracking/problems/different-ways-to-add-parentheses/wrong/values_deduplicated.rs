pub fn diff_ways_to_compute(expression: &str) -> Vec<i64> {
    fn ways(nums: &[i64], ops: &[u8]) -> std::collections::BTreeSet<i64> {
        if ops.is_empty() {
            return [nums[0]].into();
        }
        let mut out = std::collections::BTreeSet::new();
        for i in 0..ops.len() {
            for &a in &ways(&nums[..=i], &ops[..i]) {
                for &b in &ways(&nums[i + 1..], &ops[i + 1..]) {
                    out.insert(match ops[i] { b'+' => a + b, b'-' => a - b, _ => a * b });
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
    ways(&nums, &ops).into_iter().collect()
}
