use solution::*;

use std::cell::RefCell;

fn run() -> Vec<&'static str> {
    let log = RefCell::new(Vec::new());
    scene(&log);
    log.into_inner()
}

#[test]
fn prediction_matches_the_run() {
    check!("scene()", PREDICTED.to_vec(), run());
}

#[test]
fn twelve_names() {
    check!("names filled in", PREDICTED.iter().filter(|n| **n != "?").count(), 12);
}

#[test]
fn known_names() {
    let mut p = PREDICTED.to_vec();
    p.sort();
    let mut r = run();
    r.sort();
    check!("the names in PREDICTED, sorted", p, r);
}

#[test]
fn first_drop() {
    check!("the first name dropped", PREDICTED[0], run()[0]);
}

#[test]
fn last_drop() {
    check!("the last name dropped", PREDICTED[11], run()[11]);
}
