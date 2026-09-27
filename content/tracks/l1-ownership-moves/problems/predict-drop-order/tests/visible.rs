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
