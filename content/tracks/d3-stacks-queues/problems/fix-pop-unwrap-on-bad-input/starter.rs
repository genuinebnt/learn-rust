#[derive(Debug, PartialEq)]
pub enum RpnError {
    NotEnoughOperands,
    BadToken(String),
    DivideByZero,
    LeftoverOperands,
}

/// Evaluates reverse Polish notation.
pub fn eval(tokens: &[&str]) -> Result<i64, RpnError> {
    let mut stack: Vec<i64> = Vec::new();
    for &t in tokens {
        match t {
            "+" | "-" | "*" | "/" => {
                let b = stack.pop().unwrap();
                let a = stack.pop().unwrap();
                stack.push(match t {
                    "+" => a + b,
                    "-" => a - b,
                    "*" => a * b,
                    _ => a / b,
                });
            }
            _ => stack.push(t.parse().unwrap()),
        }
    }
    Ok(stack.pop().unwrap())
}
