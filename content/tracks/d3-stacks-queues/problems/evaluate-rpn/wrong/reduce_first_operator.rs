pub fn eval_rpn(tokens: &[&str]) -> i64 {
    let mut items: Vec<Result<i64, &str>> = tokens.iter().map(|t| t.parse::<i64>().map_err(|_| *t)).collect();
    while items.len() > 1 {
        let i = items.iter().position(|t| t.is_err()).expect("valid RPN");
        let (a, b) = (items[i - 2].expect("number"), items[i - 1].expect("number"));
        let v = match items[i] {
            Err("+") => a + b,
            Err("-") => a - b,
            Err("*") => a * b,
            _ => a / b,
        };
        items.splice(i - 2..=i, [Ok(v)]);
    }
    items[0].expect("valid RPN")
}
