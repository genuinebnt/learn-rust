use solution::*;

use std::cell::RefCell;

#[test]
fn prediction_matches_the_run() {
    let log = RefCell::new(Vec::new());
    scene(&log);
    check!("scene()", PREDICTED.to_vec(), log.into_inner());
}

#[test]
fn six_names() {
    check!(r#"PREDICTED"#, PREDICTED.iter().filter(|n| **n != "?").count(), 6);
}

#[test]
fn known_names() {
    check!(r#"PREDICTED"#, PREDICTED.iter().all(|n| ["a", "b", "c", "first", "second", "ignored"].contains(n)), true);
}

#[test]
fn first_drop() {
    let log = RefCell::new(Vec::new());
    scene(&log);
    check!("the first name dropped", PREDICTED[0], log.into_inner()[0]);
}

#[test]
fn last_drop() {
    let log = RefCell::new(Vec::new());
    scene(&log);
    check!("the last name dropped", PREDICTED[5], log.into_inner()[5]);
}
