use solution::*;

#[test]
fn four() {
    check!(r#"[3,6,7,11], 8 hours"#, min_eating_speed(&[3, 6, 7, 11], 8), Some(4));
}

#[test]
fn tight() {
    check!(r#"[30,11,23,4,20], 5 hours"#, min_eating_speed(&[30, 11, 23, 4, 20], 5), Some(30));
}

#[test]
fn six_hours() {
    check!(r#"[30,11,23,4,20], 6 hours"#, min_eating_speed(&[30, 11, 23, 4, 20], 6), Some(23));
}

#[test]
fn fewer_hours_than_piles() {
    check!(r#"[1,1,1], 2 hours"#, min_eating_speed(&[1, 1, 1], 2), None);
}

#[test]
fn leftover_still_costs_an_hour() {
    check!(r#"[10], 3 hours"#, min_eating_speed(&[10], 3), Some(4));
}
