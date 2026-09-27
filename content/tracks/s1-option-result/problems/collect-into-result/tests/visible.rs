use solution::*;

#[test]
fn parse_all_good_and_bad() {
    check!(r#"["1", "2", "3"] and ["1", "x", "y"]"#, (parse_all(&["1", "2", "3"]), parse_all(&["1", "x", "y"])), (Ok(vec![1, 2, 3]), Err("bad number: x".to_string())));
}

#[test]
fn sum_does_not_overflow_i32() {
    check!(r#"["2147483647", "2147483647"]"#, sum_all(&["2147483647", "2147483647"]), Ok(4_294_967_294));
}

#[test]
fn every_error() {
    check!(r#"["1", "x", "2", "y"]"#, parse_every_error(&["1", "x", "2", "y"]), Err(vec!["bad number: x".to_string(), "bad number: y".to_string()]));
}

#[test]
fn validate_stops_at_the_first_error() {
    let mut seen = Vec::new();
    let r = validate(&["a", "bad", "c", "bad2"], |s| {
        seen.push(s.to_string());
        if s.starts_with("bad") { Err(s.to_string()) } else { Ok(()) }
    });
    check!(r#"items a, bad, c, bad2; check fails on "bad…""#, (r, seen), (Err("bad".to_string()), vec!["a".to_string(), "bad".to_string()]));
}

#[test]
fn no_items() {
    check!(r#"[]"#, (parse_all(&[]), sum_all(&[]), parse_every_error(&[]), validate(&[], |_| Err("never".to_string()))), (Ok(vec![]), Ok(0), Ok(vec![]), Ok(())));
}
