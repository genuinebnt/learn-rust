use solution::*;

#[test]
fn empty_line() {
    check!(r#""""#, sum_csv(""), Ok(0));
}

#[test]
fn lone_comma() {
    check!(r#"",""#, sum_csv(","), Err(CsvError::Empty(1)));
}

#[test]
fn two_trailing_commas() {
    check!(r#""1,2,,""#, sum_csv("1,2,,"), Err(CsvError::Empty(3)));
}

#[test]
fn trailing_comma_then_space() {
    check!(r#""1,2, ""#, sum_csv("1,2, "), Err(CsvError::Empty(3)));
}

#[test]
fn blank_field() {
    check!(r#""   ""#, sum_csv("   "), Err(CsvError::Empty(1)));
}

#[test]
fn first_problem_wins() {
    check!(r#""1,x,,y""#, sum_csv("1,x,,y"), Err(CsvError::Bad(2, "x".to_string())));
}

#[test]
fn float_is_bad() {
    check!(r#""1.5""#, sum_csv("1.5"), Err(CsvError::Bad(1, "1.5".to_string())));
}

#[test]
fn inner_space_is_bad() {
    check!(r#""1 2,3""#, sum_csv("1 2,3"), Err(CsvError::Bad(1, "1 2".to_string())));
}

#[test]
fn signs_and_tabs() {
    check!(r#""\t+5\t,-7\n""#, sum_csv("\t+5\t,-7\n"), Ok(-2));
}

#[test]
fn beyond_i32() {
    check!(r#""3000000000,3000000000""#, sum_csv("3000000000,3000000000"), Ok(6_000_000_000));
}

#[test]
fn i64_bounds() {
    check!(r#""9223372036854775807,-9223372036854775808""#, sum_csv("9223372036854775807,-9223372036854775808"), Ok(-1));
}

#[test]
fn running_total_overflows() {
    check!(r#""9223372036854775807,1,-1""#, sum_csv("9223372036854775807,1,-1"), Err(CsvError::Overflow));
}

#[test]
fn field_too_big() {
    check!(r#""9223372036854775808""#, sum_csv("9223372036854775808"), Err(CsvError::Bad(1, "9223372036854775808".to_string())));
}

#[test]
fn log_without_millis() {
    check!(r#""d t INFO started""#, parse_log("d t INFO started"), Some(LogLine { date: "d", time: "t", level: "INFO", message: "started", millis: None }));
}

#[test]
fn log_missing_message() {
    check!(r#""d t INFO""#, parse_log("d t INFO"), Some(LogLine { date: "d", time: "t", level: "INFO", message: "", millis: None }));
}

#[test]
fn log_empty_message() {
    check!(r#""d t INFO ""#, parse_log("d t INFO "), Some(LogLine { date: "d", time: "t", level: "INFO", message: "", millis: None }));
}

#[test]
fn log_too_short() {
    check!(r#""d t" and """#, (parse_log("d t"), parse_log("")), (None, None));
}

#[test]
fn log_double_space() {
    check!(r#""d  t INFO x" (empty time)"#, parse_log("d  t INFO x"), None);
}

#[test]
fn log_millis_only_message() {
    check!(r#""d t DEBUG 7ms""#, parse_log("d t DEBUG 7ms"), Some(LogLine { date: "d", time: "t", level: "DEBUG", message: "7ms", millis: Some(7) }));
}

#[test]
fn log_millis_must_be_last() {
    check!(r#""d t INFO 5ms later""#, parse_log("d t INFO 5ms later"), Some(LogLine { date: "d", time: "t", level: "INFO", message: "5ms later", millis: None }));
}

#[test]
fn log_millis_digits_only() {
    check!(r#""d t I x +5ms", "d t I x ms", "d t I x 5 ms""#, [parse_log("d t I x +5ms"), parse_log("d t I x ms"), parse_log("d t I x 5 ms")].map(|l| l.unwrap().millis), [None; 3]);
}

#[test]
fn log_millis_too_big() {
    check!(r#""d t I x 18446744073709551616ms""#, parse_log("d t I x 18446744073709551616ms").unwrap().millis, None);
}

#[test]
fn log_millis_u64_max() {
    check!(r#""d t I 18446744073709551615ms""#, parse_log("d t I 18446744073709551615ms").unwrap().millis, Some(u64::MAX));
}

#[test]
fn log_unicode_message() {
    check!(r#""d t INFO café ☕ 3ms""#, parse_log("d t INFO café ☕ 3ms"), Some(LogLine { date: "d", time: "t", level: "INFO", message: "café ☕ 3ms", millis: Some(3) }));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(7202);
    let pieces = ["", " ", "7", " -3 ", "12", "x", "0", "9223372036854775807"];
    for _ in 0..400 {
        let n = rng.below(6);
        let mut fields: Vec<&str> = Vec::new();
        for _ in 0..n {
            fields.push(*rng.pick(&pieces));
        }
        let mut line = fields.join(",");
        if rng.bool() {
            line.push(',');
        }
        let mut want = Ok(0i64);
        let mut cut: Vec<&str> = line.split(',').collect();
        if line.ends_with(',') {
            cut.pop();
        }
        if line.is_empty() {
            cut.clear();
        }
        for (i, f) in cut.iter().enumerate() {
            let f = f.trim();
            let step = if f.is_empty() {
                Err(CsvError::Empty(i + 1))
            } else {
                match f.parse::<i64>() {
                    Err(_) => Err(CsvError::Bad(i + 1, f.to_string())),
                    Ok(v) => want.as_ref().ok().and_then(|t: &i64| t.checked_add(v)).ok_or(CsvError::Overflow),
                }
            };
            match step {
                Ok(t) => want = Ok(t),
                Err(e) => {
                    want = Err(e);
                    break;
                }
            }
        }
        check!(format!("line = {line:?}"), sum_csv(&line), want);
    }
}

#[test]
fn scale_200k_fields() {
    let line = "1, ".repeat(200_000);
    check!("line = \"1, 1, …\" (200000 fields, then a trailing space)", sum_csv(&line), Err(CsvError::Empty(200_001)));
    let line = "1,".repeat(200_000);
    check!("line = \"1,1,…,\" (200000 fields and a trailing comma)", sum_csv(&line), Ok(200_000));
}
