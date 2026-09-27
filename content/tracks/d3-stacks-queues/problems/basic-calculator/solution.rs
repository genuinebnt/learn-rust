pub fn calculate(s: &str) -> i64 {
    // On '(': save the running sum and the sign in front of the parenthesis.
    let mut saved: Vec<(i64, i64)> = Vec::new();
    let (mut sum, mut sign, mut num) = (0i64, 1i64, 0i64);
    for b in s.bytes() {
        match b {
            b'0'..=b'9' => num = num * 10 + i64::from(b - b'0'),
            b'+' | b'-' => {
                sum += sign * num;
                num = 0;
                sign = if b == b'+' { 1 } else { -1 };
            }
            b'(' => {
                saved.push((sum, sign));
                sum = 0;
                sign = 1;
            }
            b')' => {
                sum += sign * num;
                num = 0;
                let (outer, outer_sign) = saved.pop().expect("balanced parentheses");
                sum = outer + outer_sign * sum;
                sign = 1;
            }
            _ => {}
        }
    }
    sum + sign * num
}
