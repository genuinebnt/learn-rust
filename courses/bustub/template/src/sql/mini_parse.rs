//! A precedence-climbing evaluator for + - * / over integers.

fn tokens(s: &str) -> Option<Vec<String>> {
    let mut v = Vec::new();
    let mut cur = String::new();
    for c in s.chars() {
        if c.is_ascii_digit() {
            cur.push(c);
        } else {
            if !cur.is_empty() {
                v.push(std::mem::take(&mut cur));
            }
            match c {
                ' ' => {}
                '+' | '-' | '*' | '/' | '(' | ')' => v.push(c.to_string()),
                _ => return None,
            }
        }
    }
    if !cur.is_empty() {
        v.push(cur);
    }
    Some(v)
}

fn prec(op: &str) -> Option<u8> {
    match op {
        "+" | "-" => Some(1),
        "*" | "/" => Some(2),
        _ => None,
    }
}

fn atom(t: &[String], i: &mut usize) -> Option<i64> {
    let tok = t.get(*i)?;
    *i += 1;
    if tok == "(" {
        let v = expr(t, i, 1)?;
        if t.get(*i)? != ")" {
            return None;
        }
        *i += 1;
        Some(v)
    } else {
        tok.parse().ok()
    }
}

fn expr(t: &[String], i: &mut usize, min_prec: u8) -> Option<i64> {
    let mut lhs = atom(t, i)?;
    while let Some(op) = t.get(*i) {
        let Some(p) = prec(op) else { break };
        if p < min_prec {
            break;
        }
        *i += 1;
        let rhs = expr(t, i, p)?;
        lhs = match op.as_str() {
            "+" => lhs.checked_add(rhs)?,
            "-" => lhs.checked_sub(rhs)?,
            "*" => lhs.checked_mul(rhs)?,
            _ => lhs.checked_div(rhs)?,
        };
    }
    Some(lhs)
}

/// Parses and evaluates; `None` for a syntax error, overflow or division by zero.
pub fn parse_and_eval(s: &str) -> Option<i64> {
    let t = tokens(s)?;
    let mut i = 0;
    let v = expr(&t, &mut i, 1)?;
    if i == t.len() {
        Some(v)
    } else {
        None
    }
}
