pub fn eval_rpn(tokens: &[&str]) -> i64 {
    let mut stack: Vec<i64> = Vec::new();
    for &t in tokens {
        if let Ok(n) = t.parse::<i64>() {
            stack.push(n);
            continue;
        }
        let a = stack.pop().expect("valid RPN");
            let b = stack.pop().expect("valid RPN");
        stack.push(match t {
            "+" => a + b,
            "-" => a - b,
            "*" => a * b,
            "/" => a / b,
            _ => panic!("unknown operator {t}"),
        });
    }
    i64::from(stack.pop().expect("valid RPN"))
}
