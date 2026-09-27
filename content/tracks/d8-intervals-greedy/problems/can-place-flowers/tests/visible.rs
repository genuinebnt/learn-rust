use solution::*;

/// "10001" → [true, false, false, false, true]
fn bed(s: &str) -> Vec<bool> {
    s.bytes().map(|b| b == b'1').collect()
}

#[test]
fn leetcode_one() {
    check!(r#"bed = [1, 0, 0, 0, 1], n = 1"#, can_place_flowers(&bed("10001"), 1), true);
}

#[test]
fn leetcode_two() {
    check!(r#"bed = [1, 0, 0, 0, 1], n = 2"#, can_place_flowers(&bed("10001"), 2), false);
}

#[test]
fn empty_bed_zero() {
    check!(r#"bed = [], n = 0"#, can_place_flowers(&[], 0), true);
}

#[test]
fn empty_bed_one() {
    check!(r#"bed = [], n = 1"#, can_place_flowers(&[], 1), false);
}

#[test]
fn single_empty_plot() {
    check!(r#"bed = [0], n = 1"#, can_place_flowers(&bed("0"), 1), true);
}

#[test]
fn ends_count_as_empty() {
    check!(r#"bed = [0, 0, 1, 0, 0], n = 2"#, can_place_flowers(&bed("00100"), 2), true);
}

#[test]
fn zero_flowers_always_fit() {
    check!(r#"bed = [1], n = 0"#, can_place_flowers(&bed("1"), 0), true);
}
