use solution::*;

#[test]
fn max() {
    check!(r#"s = "2147483647""#, my_atoi("2147483647"), i32::MAX);
}

#[test]
fn one_past_max() {
    check!(r#"s = "2147483648""#, my_atoi("2147483648"), i32::MAX);
}

#[test]
fn exact_min() {
    check!(r#"s = "-2147483648""#, my_atoi("-2147483648"), i32::MIN);
}

#[test]
fn one_past_min() {
    check!(r#"s = "-2147483649""#, my_atoi("-2147483649"), i32::MIN);
}

#[test]
fn two_signs() {
    check!(r#"s = "+-12""#, my_atoi("+-12"), 0);
}

#[test]
fn plus() {
    check!(r#"s = "+1""#, my_atoi("+1"), 1);
}

#[test]
fn tab_is_not_a_space() {
    check!(r#"s = "\t42""#, my_atoi("\t42"), 0);
}

#[test]
fn space_after_sign() {
    check!(r#"s = " - 1""#, my_atoi(" - 1"), 0);
}

#[test]
fn space_inside_digits() {
    check!(r#"s = "   +0 123""#, my_atoi("   +0 123"), 0);
}

#[test]
fn many_leading_zeros() {
    check!(r#"s = "00000000000012345678""#, my_atoi("00000000000012345678"), 12345678);
}

#[test]
fn thirty_nines() {
    check!(r#"s = '9' × 30"#, my_atoi(&"9".repeat(30)), i32::MAX);
}

#[test]
fn negative_thirty_nines() {
    check!(r#"s = "-" + '9' × 30"#, my_atoi(&format!("-{}", "9".repeat(30))), i32::MIN);
}

#[test]
fn sign_only() {
    check!(r#"s = "-""#, my_atoi("-"), 0);
}

#[test]
fn only_spaces() {
    check!(r#"s = "   ""#, my_atoi("   "), 0);
}

#[test]
fn fullwidth_digits() {
    check!(r#"s = "１２" (not ASCII digits)"#, my_atoi("１２"), 0);
}

#[test]
fn arabic_indic_digit() {
    check!(r#"s = "٣""#, my_atoi("٣"), 0);
}

#[test]
fn decimal_point() {
    check!(r#"s = "3.14""#, my_atoi("3.14"), 3);
}

#[test]
fn negative_zero() {
    check!(r#"s = "-0""#, my_atoi("-0"), 0);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(1016);
    for _ in 0..400 {
        let len = rng.below(14);
        let s = rng.string(len, " +-0123456789a9");
        // Reference: collect the digits, then do the arithmetic in i128 (at most 14 digits fit easily).
        let t = s.trim_start_matches(' ');
        let (sign, rest) = match t.as_bytes().first() {
            Some(b'-') => (-1i128, &t[1..]),
            Some(b'+') => (1i128, &t[1..]),
            _ => (1i128, t),
        };
        let digits: String = rest.chars().take_while(|c| c.is_ascii_digit()).collect();
        let v = if digits.is_empty() { 0 } else { sign * digits.parse::<i128>().unwrap() };
        let want = v.clamp(i128::from(i32::MIN), i128::from(i32::MAX)) as i32;
        check!(format!("s = {s:?}"), my_atoi(&s), want);
    }
}

#[test]
fn long_inputs() {
    let zeros = format!("{}42", "0".repeat(1_000_000));
    let spaces = format!("{}-7", " ".repeat(1_000_000));
    let nines = "9".repeat(1_000_000);
    check!("s = '0' × 10⁶ + \"42\"; ' ' × 10⁶ + \"-7\"; '9' × 10⁶", (my_atoi(&zeros), my_atoi(&spaces), my_atoi(&nines)), (42, -7, i32::MAX));
}
