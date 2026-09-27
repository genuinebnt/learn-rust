use solution::*;

#[test]
fn parse_error_kept() {
    check!(r#""a=x""#, sum_config("a=x").unwrap_err().is::<std::num::ParseIntError>(), true);
}

#[test]
fn negatives() {
    check!(r#""a=-5\nb=2""#, sum_config("a=-5\nb=2").ok(), Some(-3));
}

#[test]
fn only_blank_lines() {
    check!(r#""\n  \n\t""#, sum_config("\n  \n\t").ok(), Some(0));
}

#[test]
fn first_equals_splits() {
    check!(r#""a=b=1""#, sum_config("a=b=1").unwrap_err().is::<std::num::ParseIntError>(), true);
}

#[test]
fn empty_key() {
    check!(r#""=5""#, sum_config("=5").ok(), Some(5));
}

#[test]
fn empty_value() {
    check!(r#""a=""#, sum_config("a=").unwrap_err().is::<std::num::ParseIntError>(), true);
}

#[test]
fn crlf() {
    check!(r#""a=1\r\nb=2\r\n""#, sum_config("a=1\r\nb=2\r\n").ok(), Some(3));
}

#[test]
fn value_past_i64() {
    check!(r#""a=9223372036854775808""#, sum_config("a=9223372036854775808").unwrap_err().is::<std::num::ParseIntError>(), true);
}

#[test]
fn first_error_wins() {
    check!(r#""x\na=q""#, bad_line(&*sum_config("x\na=q").unwrap_err()), Some(1));
}

#[test]
fn plain_error_is_not_config() {
    check!(r#"a boxed io::Error"#, bad_line(&std::io::Error::other("boom")), None);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(314);
    for _ in 0..300 {
        let n = rng.below(6);
        let mut lines = Vec::new();
        let mut want: Result<i64, Option<usize>> = Ok(0);
        for i in 0..n {
            let line = match rng.below(4) {
                0 => String::new(),
                1 => format!("k{i}"),
                2 => format!("k = {}", rng.int(-99, 99)),
                _ => format!("k={}", rng.string(1, "x7")),
            };
            if let Ok(total) = want {
                if !line.trim().is_empty() {
                    want = match line.split_once('=') {
                        None => Err(Some(i + 1)),
                        Some((_, v)) => v.trim().parse::<i64>().map(|v| total + v).map_err(|_| None),
                    };
                }
            }
            lines.push(line);
        }
        let text = lines.join("\n");
        let got = sum_config(&text).map_err(|e| bad_line(&*e));
        check!(format!("text = {text:?}"), got, want);
    }
}

#[test]
fn parse_error_has_no_line() {
    check!(r#""a=x""#, bad_line(&*sum_config("a=x").unwrap_err()), None);
}

#[test]
fn blank_lines() {
    check!(r#""a=1\n\n b=2 ""#, sum_config("a=1\n\n b=2 ").ok(), Some(3));
}

#[test]
fn line_numbers_count_blanks() {
    check!(r#""\n\nx""#, bad_line(&*sum_config("\n\nx").unwrap_err()), Some(3));
}

#[test]
fn message() {
    check!(r#""x""#, sum_config("x").unwrap_err().to_string(), "line 1: expected key=value".to_string());
}
