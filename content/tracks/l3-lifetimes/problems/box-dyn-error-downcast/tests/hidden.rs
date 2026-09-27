use solution::*;

#[test]
fn empty() {
    check!(r#""""#, sum_config("").ok(), Some(0));
}

#[test]
fn negative() {
    check!(r#""a=-5\nb=2""#, sum_config("a=-5\nb=2").ok(), Some(-3));
}

#[test]
fn first_error_wins() {
    check!(r#""a=x\nnope""#, sum_config("a=x\nnope").map_err(|e| bad_line(&*e)), Err(Some(1)));
}

#[test]
fn blank_lines_count() {
    check!(r#""\n \nq""#, sum_config("\n \nq").map_err(|e| bad_line(&*e)), Err(Some(3)));
}

#[test]
fn overflow_is_a_source() {
    check!(r#""a=99999999999999999999""#, sum_config("a=99999999999999999999").map_err(|e| chain(&*e).len()), Err(2));
}

#[test]
fn root_of_a_leaf() {
    check!(r#"root_cause of a ConfigError without a source"#, root_cause(&ConfigError { line: 4, source: None }).to_string(), "line 4: expected key=value".to_string());
}

#[test]
fn chain_without_source() {
    check!(r#"chain of a missing '='"#, chain(&*sum_config("k").unwrap_err()), vec!["line 1: expected key=value".to_string()]);
}

#[test]
fn error_is_send_sync() {
    let e = sum_config("a=b").unwrap_err();
    check!(r#"the boxed error can cross threads"#, std::thread::spawn(move || e.to_string()).join().unwrap(), "line 1: bad number".to_string());
}

#[derive(Debug)]
struct Loading(ConfigError);

impl std::fmt::Display for Loading {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        write!(f, "loading failed")
    }
}

impl std::error::Error for Loading {
    fn source(&self) -> Option<&(dyn std::error::Error + 'static)> {
        Some(&self.0)
    }
}

#[test]
fn three_level_chain() {
    let inner = "q".parse::<i64>().unwrap_err();
    let e = Loading(ConfigError { line: 7, source: Some(inner) });
    check!("Loading(line 7: bad number(invalid digit)): chain", chain(&e), vec!["loading failed".to_string(), "line 7: bad number".to_string(), "invalid digit found in string".to_string()]);
    check!("root cause is the ParseIntError", root_cause(&e).downcast_ref::<std::num::ParseIntError>().is_some(), true);
    check!("bad_line of the outer error", bad_line(&e), None);
}

#[test]
fn second_equals_is_value() {
    check!(r#""a=b=1" (value "b=1")"#, sum_config("a=b=1").map_err(|e| bad_line(&*e)), Err(Some(1)));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(6311);
    for _ in 0..300 {
        let n = rng.below(5);
        let mut lines = Vec::new();
        for _ in 0..n {
            lines.push(match rng.below(5) {
                0 => String::new(),
                1 => "junk".to_string(),
                2 => "k=zz".to_string(),
                _ => format!("k={}", rng.int(-50, 50)),
            });
        }
        let text = lines.join("\n");
        let mut want: Result<i64, (usize, bool)> = Ok(0);
        for (i, l) in lines.iter().enumerate() {
            if l.trim().is_empty() {
                continue;
            }
            match l.split_once('=') {
                None => {
                    want = Err((i + 1, false));
                    break;
                }
                Some((_, v)) => match v.trim().parse::<i64>() {
                    Ok(x) => want = want.map(|t| t + x),
                    Err(_) => {
                        want = Err((i + 1, true));
                        break;
                    }
                },
            }
        }
        let got = sum_config(&text).map_err(|e| (bad_line(&*e).unwrap(), e.source().is_some()));
        check!(format!("config {text:?}"), got, want);
    }
}
