use solution::Inventory;

#[test]
fn boundary_at_five_is_not_low() {
    let mut inv = Inventory::new(&[("washers", 5), ("pins", 4)]);
    inv.restock_low();
    check!("washers 5, pins 4", (inv.qty("washers"), inv.qty("pins"), inv.log().len()), (Some(5), Some(14), 1));
}

#[test]
fn restocking_twice_only_logs_once() {
    let mut inv = Inventory::new(&[("bolts", 0)]);
    inv.restock_low();
    inv.restock_low();
    check!("bolts 0, restock twice", (inv.qty("bolts"), inv.log().len()), (Some(10), 1));
}
