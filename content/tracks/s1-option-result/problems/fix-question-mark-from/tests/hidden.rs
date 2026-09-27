use solution::*;

#[test]
fn empty_input() {
    check!(r#"s = """#, size(""), Err(SizeError::Missing("width")));
}

#[test]
fn empty_value() {
    check!(r#"s = "width=;height=1""#, size("width=;height=1"), Err(SizeError::BadInt("".parse::<u32>().unwrap_err())));
}

#[test]
fn negative_height() {
    check!(r#"s = "width=80;height=-1""#, size("width=80;height=-1"), Err(SizeError::BadInt("-1".parse::<u32>().unwrap_err())));
}

#[test]
fn width_overflows() {
    check!(r#"s = "width=4294967296;height=1""#, size("width=4294967296;height=1"), Err(SizeError::BadInt("4294967296".parse::<u32>().unwrap_err())));
}

#[test]
fn bounds() {
    check!(r#"s = "width=4294967295;height=0;scale=-0.5""#, size("width=4294967295;height=0;scale=-0.5"), Ok((u32::MAX, 0, -0.5)));
}

#[test]
fn empty_scale() {
    check!(r#"s = "width=1;height=2;scale=""#, size("width=1;height=2;scale="), Err(SizeError::BadFloat("".parse::<f64>().unwrap_err())));
}

#[test]
fn int_scale_is_fine() {
    check!(r#"s = "scale=3;width=1;height=2""#, size("scale=3;width=1;height=2"), Ok((1, 2, 3.0)));
}

#[test]
fn bad_width_before_missing_height() {
    check!(r#"s = "width=x""#, size("width=x"), Err(SizeError::BadInt("x".parse::<u32>().unwrap_err())));
}

#[test]
fn missing_width_before_bad_height() {
    check!(r#"s = "height=x""#, size("height=x"), Err(SizeError::Missing("width")));
}

#[test]
fn int_error_before_float_error() {
    check!(r#"s = "scale=z;width=1;height=y""#, size("scale=z;width=1;height=y"), Err(SizeError::BadInt("y".parse::<u32>().unwrap_err())));
}

#[test]
fn first_width_wins() {
    check!(r#"s = "width=1;width=2;height=3""#, size("width=1;width=2;height=3"), Ok((1, 3, 1.0)));
}

#[test]
fn full_width_digit() {
    check!(r#"s = "width=８;height=1""#, size("width=８;height=1"), Err(SizeError::BadInt("８".parse::<u32>().unwrap_err())));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1315);
    let values = ["0", "7", "42", "-1", "", "x", "4294967295", "4294967296", "+3", "2.5", "1e3"];
    for _ in 0..300 {
        let w = rng.bool().then(|| *rng.pick(&values));
        let h = rng.bool().then(|| *rng.pick(&values));
        let sc = rng.bool().then(|| *rng.pick(&values));
        let mut parts: Vec<String> = Vec::new();
        for (name, v) in [("width", w), ("height", h), ("scale", sc)] {
            if let Some(v) = v {
                parts.push(format!("{name}={v}"));
            }
        }
        rng.shuffle(&mut parts);
        let s = parts.join(";");
        let int = |v: Option<&str>, name: &'static str| v.ok_or(SizeError::Missing(name))?.parse::<u32>().map_err(SizeError::BadInt);
        let want = int(w, "width").and_then(|x| {
            let y = int(h, "height")?;
            let z = sc.map_or(Ok(1.0), |v| v.parse::<f64>().map_err(SizeError::BadFloat))?;
            Ok((x, y, z))
        });
        check!(format!("s = {s:?}"), size(&s), want);
    }
}
