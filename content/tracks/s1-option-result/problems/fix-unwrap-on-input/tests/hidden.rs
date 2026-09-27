use solution::*;

#[test]
fn whitespace_only() {
    check!(r#""   ""#, average("   "), Err("no numbers".to_string()));
}

#[test]
fn trailing_comma() {
    check!(r#""4,""#, average("4,"), Err("not a number: ".to_string()));
}

#[test]
fn negatives_and_decimals() {
    check!(r#""-1.5, 2.5""#, average("-1.5, 2.5"), Ok(0.5));
}

#[test]
fn no_spaces() {
    check!(r#""1,2""#, average("1,2"), Ok(1.5));
}

#[test]
fn spaces_around_items() {
    check!(r#""  1 ,\t2  ""#, average("  1 ,\t2  "), Ok(1.5));
}

#[test]
fn message_is_trimmed() {
    check!(r#""1,   x  ""#, average("1,   x  "), Err("not a number: x".to_string()));
}

#[test]
fn first_bad_item_wins() {
    check!(r#""a, b""#, average("a, b"), Err("not a number: a".to_string()));
}

#[test]
fn only_a_comma() {
    check!(r#"",""#, average(","), Err("not a number: ".to_string()));
}

#[test]
fn unicode_item() {
    check!(r#""1, ２""#, average("1, ２"), Err("not a number: ２".to_string()));
}

#[test]
fn nan_is_not_a_number() {
    check!(r#""1, NaN""#, average("1, NaN"), Err("not a number: NaN".to_string()));
}

#[test]
fn infinities_are_not_numbers() {
    check!(r#""inf", "-infinity""#, (average("inf"), average("2, -infinity")), (Err("not a number: inf".to_string()), Err("not a number: -infinity".to_string())));
}

#[test]
fn overflowing_literal() {
    check!(r#""1e999""#, average("1e999"), Err("not a number: 1e999".to_string()));
}

#[test]
fn large_but_finite() {
    check!(r#""1e300, -1e300, 3""#, average("1e300, -1e300, 3"), Ok(1.0));
}

#[test]
fn exponents_and_signs() {
    check!(r#""+1.5e1, -5""#, average("+1.5e1, -5"), Ok(5.0));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1308);
    for _ in 0..400 {
        let n = rng.below(6);
        let mut items: Vec<String> = Vec::new();
        for _ in 0..n {
            let item = if rng.below(8) == 0 { (*rng.pick(&["x", "", "1x"])).to_string() } else { rng.int(-9, 9).to_string() };
            let pad = rng.below(3);
            items.push(format!("{}{}{}", " ".repeat(pad), item, " ".repeat(2 - pad)));
        }
        let input = items.join(",");
        let want = if input.trim().is_empty() {
            Err("no numbers".to_string())
        } else if let Some(bad) = items.iter().map(|s| s.trim()).find(|s| s.parse::<i32>().is_err()) {
            Err(format!("not a number: {bad}"))
        } else {
            let sum: i32 = items.iter().map(|s| s.trim().parse::<i32>().unwrap_or(0)).sum();
            Ok(f64::from(sum) / items.len() as f64)
        };
        check!(format!("input = {input:?}"), average(&input), want);
    }
}
