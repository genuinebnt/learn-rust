use solution::*;

fn show(rs: &[Reading]) -> Vec<String> {
    rs.iter().map(|r| r.0.to_string()).collect()
}

#[test]
fn top_two() {
    check!(r#"readings = [3.5, -1.0, 9.25, 2.0], k = 2"#, show(&top_k(&[3.5, -1.0, 9.25, 2.0], 2)), vec!["9.25", "3.5"]);
}

#[test]
fn nan_is_skipped() {
    check!(r#"readings = [NaN, 1.0, NaN, -4.0], k = 3"#, show(&top_k(&[f64::NAN, 1.0, f64::NAN, -4.0], 3)), vec!["1", "-4"]);
}

#[test]
fn positive_zero_ranks_higher() {
    check!(r#"readings = [-0.0, 0.0], k = 1"#, show(&top_k(&[-0.0, 0.0], 1)), vec!["0"]);
}

#[test]
fn nan_equals_itself() {
    check!(r#"Reading(NaN) == Reading(NaN)"#, Reading(f64::NAN) == Reading(f64::NAN), true);
}

#[test]
fn zeros_differ() {
    check!(r#"Reading(0.0) == Reading(-0.0), Reading(-0.0) < Reading(0.0)"#, (Reading(0.0) == Reading(-0.0), Reading(-0.0) < Reading(0.0)), (false, true));
}

#[test]
fn k_zero() {
    check!(r#"readings = [1.0, 2.0], k = 0"#, show(&top_k(&[1.0, 2.0], 0)), Vec::<String>::new());
}
