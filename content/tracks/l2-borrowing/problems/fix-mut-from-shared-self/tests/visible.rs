use solution::*;

#[test]
fn receive_and_reserve() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    check!(r#"receive bolt 10, nut 4; reserve bolt 3"#, (w.reserve("bolt", 3), w.available("bolt"), w.last()), (3, 7, Some("bolt")));
}

#[test]
fn reserve_caps_at_available() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    check!(r#"receive bolt 10, nut 4; reserve nut 3, then nut 3"#, (w.reserve("nut", 3), w.reserve("nut", 3), w.available("nut")), (3, 1, 0));
}

#[test]
fn unknown_item_not_touched() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    check!(r#"receive bolt 10, nut 4; reserve ghost 1"#, (w.reserve("ghost", 1), w.last()), (0, Some("nut")));
}

#[test]
fn readers_side_by_side() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    let l = w.last();
    let a = w.available("bolt");
    check!(r#"receive bolt 10, nut 4; available(bolt) and last() held together"#, (a, l), (10, Some("nut")));
}

#[test]
fn tag_last() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.tag_last("*");
    w.tag_last("*");
    check!(r#"receive bolt 10, nut 4; tag_last "*" twice"#, (w.last(), w.available("nut"), w.available("nut*")), (Some("nut**"), 4, 0));
}

#[test]
fn ship_all_logs_sorted() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.reserve("nut", 1);
    w.reserve("bolt", 2);
    check!(r#"receive bolt 10, nut 4; reserve nut 1, bolt 2; ship_all"#, (w.ship_all(), w.log().to_vec(), w.available("bolt"), w.available("nut")), (2, vec!["bolt: 2".to_string(), "nut: 1".to_string()], 8, 3));
}

#[test]
fn count_low() {
    let mut w = Warehouse::new();
    w.receive("bolt", 10);
    w.receive("nut", 4);
    w.reserve("bolt", 7);
    check!(r#"receive bolt 10, nut 4; reserve bolt 7; count_low(4)"#, w.count_low(4), 1);
}
