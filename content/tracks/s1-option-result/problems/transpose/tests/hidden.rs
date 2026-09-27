use solution::*;

#[test]
fn negative() {
    check!(r#"s = Some("-7")"#, parse_optional(Some("-7")), Ok(Some(-7)));
}

#[test]
fn empty_string() {
    check!(r#"s = Some("")"#, parse_optional(Some("")).is_err(), true);
}

#[test]
fn zero() {
    check!(r#"s = Some("0")"#, parse_optional(Some("0")), Ok(Some(0)));
}

#[test]
fn i32_max() {
    check!(r#"s = Some("2147483647")"#, parse_optional(Some("2147483647")), Ok(Some(i32::MAX)));
}

#[test]
fn i32_min() {
    check!(r#"s = Some("-2147483648")"#, parse_optional(Some("-2147483648")), Ok(Some(i32::MIN)));
}

#[test]
fn below_i32_min() {
    check!(r#"s = Some("-2147483649")"#, parse_optional(Some("-2147483649")), Err("-2147483649".parse::<i32>().unwrap_err()));
}

#[test]
fn leading_space() {
    check!(r#"s = Some(" 5")"#, parse_optional(Some(" 5")), Err(" 5".parse::<i32>().unwrap_err()));
}

#[test]
fn decimal() {
    check!(r#"s = Some("1.0")"#, parse_optional(Some("1.0")), Err("1.0".parse::<i32>().unwrap_err()));
}

#[test]
fn keeps_the_parse_error() {
    check!(r#"s = Some("")"#, parse_optional(Some("")).map_err(|e| e.kind().clone()), Err(std::num::IntErrorKind::Empty));
}

#[test]
fn full_width_digits() {
    check!(r#"s = Some("４２")"#, parse_optional(Some("４２")).is_err(), true);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1306);
    for _ in 0..400 {
        let s = match rng.below(4) {
            0 => None,
            1 => {
                let len = rng.below(5);
                Some(rng.string(len, "01-+ x9"))
            }
            2 => Some(rng.int(-3_000_000_000, 3_000_000_000).to_string()),
            _ => Some((i64::from(i32::MAX) + rng.int(-2, 2)).to_string()),
        };
        let want = match &s {
            None => Ok(None),
            Some(t) => t.parse::<i32>().map(Some),
        };
        check!(format!("s = {s:?}"), parse_optional(s.as_deref()), want);
    }
}
