use solution::*;

fn approx(got: f64, want: f64) -> f64 {
    if got == want || (got - want).abs() <= 1e-9 * want.abs().max(1.0) {
        want
    } else {
        got
    }
}

#[test]
fn leetcode_two_to_the_ten() {
    check!(r#"x = 2.0, n = 10"#, approx(my_pow(2.0, 10), 1024.0), 1024.0);
}

#[test]
fn leetcode_fractional_base() {
    check!(r#"x = 2.1, n = 3"#, approx(my_pow(2.1, 3), 9.261), 9.261);
}

#[test]
fn leetcode_negative_exponent() {
    check!(r#"x = 2.0, n = -2"#, approx(my_pow(2.0, -2), 0.25), 0.25);
}

#[test]
fn zero_exponent_is_one() {
    check!(r#"x = 5.0, n = 0"#, approx(my_pow(5.0, 0), 1.0), 1.0);
}

#[test]
fn exponent_one() {
    check!(r#"x = 0.5, n = 1"#, approx(my_pow(0.5, 1), 0.5), 0.5);
}

#[test]
fn negative_base_odd_exponent() {
    check!(r#"x = -2.0, n = 3"#, approx(my_pow(-2.0, 3), -8.0), -8.0);
}
