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
                    _ => {
                        if b == 0 {
                            return Err(RpnError::DivideByZero);
                        }
                        a / b
                    },
                });
            }
            _ => stack.push(t.parse().map_err(|_| RpnError::BadToken(t.to_string()))?),
        }
    }
    let result = stack.pop().ok_or(RpnError::NotEnoughOperands)?;
    if !stack.is_empty() {
        return Err(RpnError::LeftoverOperands);
    }
    Ok(result)
}
