use solution::*;

use std::cell::RefCell;

#[test]
fn ignored_drops_first() {
    let log = RefCell::new(Vec::new());
    scene(&log);
    check!("first drop in scene()", PREDICTED[0], log.borrow()[0]);
}
