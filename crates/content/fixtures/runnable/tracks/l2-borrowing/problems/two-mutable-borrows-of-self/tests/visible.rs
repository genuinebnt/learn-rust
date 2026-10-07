use solution::Inventory;

#[test]
fn restock_adds_ten() {
    let mut inv = Inventory::new(&[("bolts", 2), ("nuts", 40)]);
    inv.restock_low();
    check!("bolts 2, nuts 40", (inv.qty("bolts"), inv.qty("nuts")), (Some(12), Some(40)));
}

#[test]
fn logs_each_restock() {
    let mut inv = Inventory::new(&[("bolts", 2), ("rivets", 1), ("nuts", 40)]);
    inv.restock_low();
    check!("bolts 2, rivets 1, nuts 40", inv.log(), ["restocked bolts", "restocked rivets"]);
}

#[test]
fn leaves_stocked_items() {
    let mut inv = Inventory::new(&[("nuts", 40)]);
    inv.restock_low();
    check!("nuts 40", (inv.qty("nuts"), inv.log().len()), (Some(40), 0));
}

#[test]
fn five_is_not_low() {
    let mut inv = Inventory::new(&[("washers", 5), ("pins", 4)]);
    inv.restock_low();
    check!("washers 5, pins 4", (inv.qty("washers"), inv.qty("pins")), (Some(5), Some(14)));
}

#[test]
fn empty_inventory() {
    let mut inv = Inventory::new(&[]);
    inv.restock_low();
    check!("no items", inv.log().len(), 0);
}
