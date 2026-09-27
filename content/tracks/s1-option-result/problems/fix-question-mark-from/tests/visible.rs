use solution::*;

#[test]
fn all_fields() {
    check!(r#"s = "width=80;height=24;scale=1.5""#, size("width=80;height=24;scale=1.5"), Ok((80, 24, 1.5)));
}

#[test]
fn scale_defaults_to_one() {
    check!(r#"s = "height=24;width=80""#, size("height=24;width=80"), Ok((80, 24, 1.0)));
}

#[test]
fn missing_height() {
    check!(r#"s = "width=80""#, size("width=80"), Err(SizeError::Missing("height")));
}

#[test]
fn bad_width() {
    check!(r#"s = "width=abc;height=1""#, size("width=abc;height=1"), Err(SizeError::BadInt("abc".parse::<u32>().unwrap_err())));
}

#[test]
fn bad_scale() {
    check!(r#"s = "width=1;height=1;scale=big""#, size("width=1;height=1;scale=big"), Err(SizeError::BadFloat("big".parse::<f64>().unwrap_err())));
}
