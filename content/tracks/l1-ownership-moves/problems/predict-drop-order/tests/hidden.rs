use solution::*;

use std::cell::RefCell;

fn run() -> Vec<&'static str> {
    let log = RefCell::new(Vec::new());
    scene(&log);
    log.into_inner()
}

fn before(names: &[&str], x: &str, y: &str) -> bool {
    let at = |n: &str| names.iter().position(|m| *m == n);
    at(x) < at(y)
}

fn same_order(x: &str, y: &str) -> (bool, bool) {
    (before(&PREDICTED, x, y), before(&run(), x, y))
}

#[test]
fn explicit_drop_second() {
    check!("second drop: drop(a)", PREDICTED[1], run()[1]);
}

#[test]
fn arm_local_before_scrutinee_temporary() {
    let (p, r) = same_order("inner", "scrutinee");
    check!("inner before scrutinee?", p, r);
}

#[test]
fn let_underscore_does_not_move() {
    let (p, r) = same_order("c", "b");
    check!("c before b? (`let _ = b;`)", p, r);
}

#[test]
fn vec_elements_in_order() {
    let (p, r) = same_order("v0", "v1");
    check!("v0 before v1?", p, r);
}

#[test]
fn shadowing_does_not_drop() {
    let (p, r) = same_order("x1", "v1");
    check!("x1 before v1? (shadowed by the second _x)", p, r);
}

#[test]
fn shadowed_after_shadowing() {
    let (p, r) = same_order("x2", "x1");
    check!("x2 before x1?", p, r);
}

#[test]
fn fields_in_declaration_order() {
    let (p, r) = same_order("first", "second");
    check!("first before second?", p, r);
}

#[test]
fn pair_drops_last() {
    let r = run();
    check!("the last two drops", (PREDICTED[10], PREDICTED[11]), (r[10], r[11]));
}

#[test]
fn whole_order() {
    check!("scene()", PREDICTED.to_vec(), run());
}
