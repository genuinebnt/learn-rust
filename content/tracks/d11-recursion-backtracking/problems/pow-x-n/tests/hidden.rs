use solution::*;

fn approx(got: f64, want: f64) -> f64 {
    if got == want || (got - want).abs() <= 1e-9 * want.abs().max(1.0) {
        want
    } else {
        got
    }
}

#[test]
fn zero_base() {
    check!(r#"x = 0.0, n = 5"#, approx(my_pow(0.0, 5), 0.0), 0.0);
}

#[test]
fn zero_to_the_zero() {
    check!(r#"x = 0.0, n = 0"#, approx(my_pow(0.0, 0), 1.0), 1.0);
}

#[test]
fn negative_base_even_exponent() {
    check!(r#"x = -2.0, n = 4"#, approx(my_pow(-2.0, 4), 16.0), 16.0);
}

#[test]
fn half_to_minus_three() {
    check!(r#"x = 0.5, n = -3"#, approx(my_pow(0.5, -3), 8.0), 8.0);
}

#[test]
fn one_to_min_exponent() {
    check!(r#"x = 1.0, n = i32::MIN"#, approx(my_pow(1.0, i32::MIN), 1.0), 1.0);
}

#[test]
fn two_to_min_exponent() {
    check!(r#"x = 2.0, n = i32::MIN"#, approx(my_pow(2.0, i32::MIN), 0.0), 0.0);
}

#[test]
fn minus_one_to_min_exponent() {
    check!(r#"x = -1.0, n = i32::MIN"#, approx(my_pow(-1.0, i32::MIN), 1.0), 1.0);
}

#[test]
fn minus_one_to_max_exponent() {
    check!(r#"x = -1.0, n = i32::MAX"#, approx(my_pow(-1.0, i32::MAX), -1.0), -1.0);
}

#[test]
fn half_to_max_exponent() {
    check!(r#"x = 0.5, n = i32::MAX"#, approx(my_pow(0.5, i32::MAX), 0.0), 0.0);
}

#[test]
fn small_answer() {
    check!(r#"x = 0.1, n = 5"#, approx(my_pow(0.1, 5), 1e-5), 1e-5);
}

#[test]
fn random_vs_powi() {
    let mut rng = anneal_prelude::Rng::new(1101);
    for _ in 0..400 {
        let x = rng.int(-200, 200) as f64 / 100.0;
        let n = rng.int(-20, 20) as i32;
        let want = x.powi(n);
        check!(format!("x = {x}, n = {n}"), approx(my_pow(x, n), want), want);
    }
}

#[test]
fn scale_huge_exponents() {
    let got = (my_pow(1.0, i32::MAX), my_pow(-1.0, i32::MAX - 2), my_pow(1.0, i32::MIN + 1), my_pow(0.5, i32::MAX - 1), my_pow(-1.0, i32::MIN + 3));
    check!("x = ±1.0 or 0.5, n near i32::MAX / i32::MIN", got, (1.0, -1.0, 1.0, 0.0, -1.0));
}
