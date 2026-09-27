pub fn add_operators(num: &str, target: i64) -> Vec<String> {
    fn build(digits: &[u8], i: usize, target: i64, value: i64, last: i64, expr: &mut String, out: &mut Vec<String>) {
        if i == digits.len() {
            if value == target {
                out.push(expr.clone());
            }
            return;
        }
        let len = expr.len();
        let mut operand = 0i64;
        for j in i..digits.len() {
            operand = operand * 10 + i64::from(digits[j] - b'0');
            let text = &digits[i..=j];
            if i == 0 {
                expr.extend(text.iter().map(|&d| d as char));
                build(digits, j + 1, target, operand, operand, expr, out);
                expr.truncate(len);
                continue;
            }
            for (op, value, last) in [
                ('+', value + operand, operand),
                ('-', value - operand, -operand),
                ('*', value - last + last * operand, last * operand),
            ] {
                expr.push(op);
                expr.extend(text.iter().map(|&d| d as char));
                build(digits, j + 1, target, value, last, expr, out);
                expr.truncate(len);
            }
        }
    }
    let mut out = Vec::new();
    build(num.as_bytes(), 0, target, 0, 0, &mut String::new(), &mut out);
    out
}
