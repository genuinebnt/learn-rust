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
                let b = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                let a = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
                stack.push(match t {
                    "+" => a + b,
                    "-" => a - b,
                    "*" => a * b,
                    _ => a.checked_div(b).ok_or(RpnError::DivideByZero)?,
                });
            }
            _ => stack.push(t.parse().map_err(|_| RpnError::BadToken(t.to_string()))?),
        }
    }
    stack.pop().ok_or(RpnError::NotEnoughOperands)
}
