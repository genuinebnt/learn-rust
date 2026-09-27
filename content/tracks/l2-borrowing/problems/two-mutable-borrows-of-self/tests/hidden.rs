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

#[test]
fn empty_inventory() {
    let mut inv = Inventory::new(&[]);
    inv.restock_low();
    check!("no items", inv.log().len(), 0);
}

#[test]
fn zero_stock() {
    let mut inv = Inventory::new(&[("gears", 0)]);
    inv.restock_low();
    check!("gears 0", (inv.qty("gears"), inv.log()), (Some(10), &["restocked gears".to_string()][..]));
}

#[test]
fn logs_in_item_order() {
    let mut inv = Inventory::new(&[("c", 1), ("a", 9), ("b", 3), ("d", 4)]);
    inv.restock_low();
    check!("c 1, a 9, b 3, d 4", inv.log(), ["restocked c", "restocked b", "restocked d"]);
}

#[test]
fn unicode_names() {
    let mut inv = Inventory::new(&[("écrous", 1), ("🔩", 2)]);
    inv.restock_low();
    check!("écrous 1, 🔩 2", inv.log(), ["restocked écrous", "restocked 🔩"]);
}

#[test]
fn huge_quantity_untouched() {
    let mut inv = Inventory::new(&[("sand", u32::MAX), ("salt", 4)]);
    inv.restock_low();
    check!("sand u32::MAX, salt 4", (inv.qty("sand"), inv.qty("salt"), inv.log().len()), (Some(u32::MAX), Some(14), 1));
}

#[test]
fn random_vs_model() {
    let mut rng = anneal_prelude::Rng::new(44);
    let names = ["bolts", "nuts", "pins", "gears", "rivets", "washers"];
    for _ in 0..200 {
        let n = rng.below(6);
        let stock: Vec<(&str, u32)> = (0..n).map(|i| (names[i], rng.int(0, 9) as u32)).collect();
        let mut inv = Inventory::new(&stock);
        inv.restock_low();
        let qtys: Vec<Option<u32>> = stock.iter().map(|&(name, _)| inv.qty(name)).collect();
        let want_qtys: Vec<Option<u32>> = stock.iter().map(|&(_, q)| Some(if q < 5 { q + 10 } else { q })).collect();
        let want_log: Vec<String> = stock.iter().filter(|&&(_, q)| q < 5).map(|&(name, _)| format!("restocked {name}")).collect();
        check!(format!("stock = {stock:?}"), (qtys, inv.log().to_vec()), (want_qtys, want_log));
    }
}
