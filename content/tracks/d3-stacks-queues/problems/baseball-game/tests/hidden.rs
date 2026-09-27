use solution::*;

#[test]
fn not_a_number() {
    check!(r#"["x"]"#, cal_points(&["x"]), None);
}

#[test]
fn cancel_nothing() {
    check!(r#"["C"]"#, cal_points(&["C"]), None);
}

#[test]
fn empty() {
    check!(r#"[]"#, cal_points(&[]), Some(0));
}

#[test]
fn plus_after_cancel() {
    check!(r#"["1","2","C","+"]"#, cal_points(&["1", "2", "C", "+"]), None);
}

#[test]
fn plus_uses_last_two() {
    check!(r#"["1","2","3","+"]"#, cal_points(&["1", "2", "3", "+"]), Some(11));
}

#[test]
fn double_negative() {
    check!(r#"["-3","D"]"#, cal_points(&["-3", "D"]), Some(-9));
}

#[test]
fn beyond_i32() {
    check!(r#"["2147483647","2147483647","+"]"#, cal_points(&["2147483647", "2147483647", "+"]), Some(8_589_934_588));
}

#[test]
fn decimal_is_invalid() {
    check!(r#"["5.0"]"#, cal_points(&["5.0"]), None);
}

#[test]
fn lowercase_d_is_invalid() {
    check!(r#"["1","d"]"#, cal_points(&["1", "d"]), None);
}

#[test]
fn empty_token() {
    check!(r#"["1",""]"#, cal_points(&["1", ""]), None);
}

#[test]
fn random_vs_model() {
    fn model(ops: &[&str]) -> Option<i64> {
        let mut s: Vec<i64> = Vec::new();
        for &op in ops {
            if op == "+" {
                if s.len() < 2 {
                    return None;
                }
                let v = s[s.len() - 1] + s[s.len() - 2];
                s.push(v);
            } else if op == "D" {
                let v = *s.last()? * 2;
                s.push(v);
            } else if op == "C" {
                s.pop()?;
            } else {
                s.push(op.parse().ok()?);
            }
        }
        Some(s.iter().sum())
    }
    let mut rng = anneal_prelude::Rng::new(3003);
    let tokens = ["+", "D", "C", "1", "-2", "7", "30", "0", "x"];
    for _ in 0..400 {
        let n = rng.below(9);
        let ops: Vec<&str> = (0..n).map(|_| *rng.pick(&tokens)).collect();
        check!(format!("ops = {ops:?}"), cal_points(&ops), model(&ops));
    }
}

#[test]
fn scale_200k() {
    let ops = vec!["1000000000"; 200_000];
    check!("200000 × \"1000000000\"", cal_points(&ops), Some(200_000_000_000_000));
}
