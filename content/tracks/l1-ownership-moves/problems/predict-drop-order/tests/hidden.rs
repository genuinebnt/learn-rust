use solution::*;

use std::cell::RefCell;

fn run() -> Vec<&'static str> {
    let log = RefCell::new(Vec::new());
    scene(&log);
    log.into_inner()
}

fn at(names: &[&str], name: &str) -> Option<usize> {
    names.iter().position(|n| *n == name)
}

#[test]
fn ignored_drops_first() {
    let log = RefCell::new(Vec::new());
    scene(&log);
    check!("first drop in scene()", PREDICTED[0], log.borrow()[0]);
}

#[test]
fn each_name_once() {
    let mut names = PREDICTED.to_vec();
    names.sort();
    names.dedup();
    check!("distinct names in PREDICTED", names.len(), 6);
}

#[test]
fn explicit_drop_second() {
    check!("second drop in scene(): drop(a)", PREDICTED[1], run()[1]);
}

#[test]
fn c_before_b() {
    let (p, r) = (PREDICTED, run());
    check!("c and b: `let _ = b;` doesn't move b", (at(&p, "c") < at(&p, "b")), (at(&r, "c") < at(&r, "b")));
}

#[test]
fn fields_in_declaration_order() {
    let (p, r) = (PREDICTED, run());
    check!("Pair's fields first and second", (at(&p, "first") < at(&p, "second")), (at(&r, "first") < at(&r, "second")));
}

#[test]
fn pair_drops_last() {
    let (p, r) = (PREDICTED, run());
    check!("the last two drops (the Pair)", (p[4], p[5]), (r[4], r[5]));
}

#[test]
fn locals_in_reverse() {
    check!("third and fourth drops in scene()", (PREDICTED[2], PREDICTED[3]), (run()[2], run()[3]));
}

#[test]
fn whole_order() {
    check!("scene()", PREDICTED.to_vec(), run());
}
