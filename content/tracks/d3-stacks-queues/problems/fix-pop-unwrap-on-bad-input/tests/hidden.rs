use solution::*;

#[test]
fn empty() {
    check!(r#"[]"#, eval(&[]), Err(RpnError::NotEnoughOperands));
}

#[test]
fn one_operand() {
    check!(r#"["1","-"]"#, eval(&["1", "-"]), Err(RpnError::NotEnoughOperands));
}

#[test]
fn bad_first() {
    check!(r#"["x"]"#, eval(&["x"]), Err(RpnError::BadToken("x".to_string())));
}

#[test]
fn order() {
    check!(r#"["3","5","-"]"#, eval(&["3", "5", "-"]), Ok(-2));
}

#[test]
fn negative_numbers() {
    check!(r#"["-3","4","*"]"#, eval(&["-3", "4", "*"]), Ok(-12));
}

#[test]
fn first_error_wins() {
    check!(r#"["1","0","/","x"]"#, eval(&["1", "0", "/", "x"]), Err(RpnError::DivideByZero));
}

#[test]
fn unknown_operator() {
    check!(r#"["1","2","%"]"#, eval(&["1", "2", "%"]), Err(RpnError::BadToken("%".to_string())));
}

#[test]
fn max() {
    check!(r#"["9223372036854775807"]"#, eval(&["9223372036854775807"]), Ok(i64::MAX));
}

#[test]
fn too_big() {
    check!(r#"["9223372036854775808"]"#, eval(&["9223372036854775808"]), Err(RpnError::BadToken("9223372036854775808".to_string())));
}

#[test]
fn empty_token() {
    check!(r#"[""]"#, eval(&[""]), Err(RpnError::BadToken(String::new())));
}

#[test]
fn division_truncates() {
    check!(r#"["-7","2","/"]"#, eval(&["-7", "2", "/"]), Ok(-3));
}

#[test]
fn random_vs_model() {
    fn model(tokens: &[&str]) -> Result<i64, RpnError> {
        let mut st: Vec<i64> = Vec::new();
        for &t in tokens {
            if ["+", "-", "*", "/"].contains(&t) {
                if st.len() < 2 {
                    return Err(RpnError::NotEnoughOperands);
                }
                let (b, a) = (st.pop().unwrap(), st.pop().unwrap());
                st.push(match t {
                    "+" => a + b,
                    "-" => a - b,
                    "*" => a * b,
                    _ if b == 0 || (a == i64::MIN && b == -1) => return Err(RpnError::DivideByZero),
                    _ => a / b,
                });
            } else {
                match t.parse() {
                    Ok(n) => st.push(n),
                    Err(_) => return Err(RpnError::BadToken(t.to_string())),
                }
            }
        }
        match st.len() {
            0 => Err(RpnError::NotEnoughOperands),
            1 => Ok(st[0]),
            _ => Err(RpnError::LeftoverOperands),
        }
    }
    let mut rng = anneal_prelude::Rng::new(3010);
    let pool = ["+", "-", "*", "/", "0", "1", "-2", "3", "7", "q"];
    for _ in 0..400 {
        let n = rng.below(7);
        let tokens: Vec<&str> = (0..n).map(|_| *rng.pick(&pool)).collect();
        check!(format!("tokens = {tokens:?}"), eval(&tokens), model(&tokens));
    }
}

#[test]
fn min_div_minus_one() {
    check!(r#"["-9223372036854775808","-1","/"]"#, eval(&["-9223372036854775808", "-1", "/"]), Err(RpnError::DivideByZero));
}
