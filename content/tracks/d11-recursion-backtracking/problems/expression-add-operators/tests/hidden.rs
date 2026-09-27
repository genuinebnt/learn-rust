use solution::*;

fn sorted<T: Ord>(mut v: Vec<T>) -> Vec<T> {
    v.sort();
    v
}

/// The value of an expression of digits, `+`, `-` and `*`, or `None` if an operand has a leading zero.
fn value(expr: &str) -> Option<i64> {
    let bytes = expr.as_bytes();
    let (mut total, mut sign, mut start) = (0i64, 1i64, 0);
    for i in 0..=bytes.len() {
        if i == bytes.len() || bytes[i] == b'+' || bytes[i] == b'-' {
            let mut product = 1i64;
            for operand in expr[start..i].split('*') {
                if operand.len() > 1 && operand.starts_with('0') {
                    return None;
                }
                product *= operand.parse::<i64>().unwrap();
            }
            total += sign * product;
            if i < bytes.len() {
                sign = if bytes[i] == b'+' { 1 } else { -1 };
            }
            start = i + 1;
        }
    }
    Some(total)
}

#[test]
fn single_zero() {
    check!(r#"num = "0", target = 0"#, add_operators("0", 0), vec!["0"]);
}

#[test]
fn single_digit() {
    check!(r#"num = "5", target = 5"#, add_operators("5", 5), vec!["5"]);
}

#[test]
fn single_digit_miss() {
    check!(r#"num = "5", target = 3"#, add_operators("5", 3), Vec::<String>::new());
}

#[test]
fn times_before_plus() {
    check!(r#"num = "123", target = 7"#, add_operators("123", 7), vec!["1+2*3"]);
}

#[test]
fn negative_target() {
    check!(r#"num = "123", target = -4"#, add_operators("123", -4), vec!["1-2-3"]);
}

#[test]
fn three_zeros() {
    check!(r#"num = "000", target = 0"#, add_operators("000", 0).len(), 9);
}

#[test]
fn leetcode_past_i32() {
    check!(r#"num = "2147483648", target = -2147483648"#, add_operators("2147483648", -2147483648), Vec::<String>::new());
}

#[test]
fn ten_nines() {
    check!(r#"num = "9999999999", target = 0: (expressions, all worth 0)"#, { let all = add_operators("9999999999", 0); (all.len(), all.iter().all(|e| value(e) == Some(0))) }, (3930, true));
}

#[test]
fn big_products() {
    check!(r#"num = "999999999", target = 81"#, sorted(add_operators("999999999", 81)), vec!["9+9+9+9+9+9+9+9+9", "999-9*99-9-9-9", "999-9-9*99-9-9", "999-9-9-9*99-9", "999-9-9-9-9*99", "999-9-9-9-99*9", "999-9-9-99*9-9", "999-9-99*9-9-9", "999-99*9-9-9-9"]);
}

/// Every way to put nothing, `+`, `-` or `*` between the digits, kept when the value is `target`.
fn brute(num: &str, target: i64) -> Vec<String> {
    let digits = num.as_bytes();
    let mut out = Vec::new();
    for mut code in 0..4usize.pow(digits.len() as u32 - 1) {
        let mut expr = String::from(digits[0] as char);
        for &d in &digits[1..] {
            match code % 4 {
                1 => expr.push('+'),
                2 => expr.push('-'),
                3 => expr.push('*'),
                _ => {}
            }
            expr.push(d as char);
            code /= 4;
        }
        if value(&expr) == Some(target) {
            out.push(expr);
        }
    }
    out
}

#[test]
fn random_vs_every_operator_choice() {
    let mut rng = anneal_prelude::Rng::new(1137);
    for _ in 0..300 {
        let len = rng.int(1, 6) as usize;
        let num = rng.string(len, "0012359");
        // Half the targets are the value of some expression, so there's an answer to find.
        let target = if rng.bool() {
            rng.int(-30, 60)
        } else {
            let ops = rng.string(len - 1, " +-*");
            let mut expr = String::new();
            for (i, d) in num.chars().enumerate() {
                if i > 0 && &ops[i - 1..i] != " " {
                    expr.push_str(&ops[i - 1..i]);
                }
                expr.push(d);
            }
            value(&expr).unwrap_or(0)
        };
        check!(format!("num = {num:?}, target = {target}"), sorted(add_operators(&num, target)), sorted(brute(&num, target)));
    }
}

#[test]
fn scale_ten_digits() {
    let all = add_operators("1234567890", 45);
    let ok = all.iter().all(|e| value(e) == Some(45));
    check!("num = \"1234567890\", target = 45: (expressions, all evaluate to 45)", (all.len(), ok), (473, true));
}

#[test]
fn scale_many_zeros() {
    let all = add_operators("1000000009", 9);
    let ok = all.iter().all(|e| value(e) == Some(9));
    check!("num = \"1000000009\", target = 9: (expressions, all valid and worth 9)", (all.len(), ok), (3280, true));
}
