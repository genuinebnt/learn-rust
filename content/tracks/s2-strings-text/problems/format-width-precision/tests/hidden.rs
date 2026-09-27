use solution::*;

#[test]
fn long_item_cut() {
    check!(r#""Cappuccino grande", 1, 4.25"#, receipt_line("Cappuccino grande", 1, 4.25), "Cappuccino  1     4.25".to_string());
}

#[test]
fn big_price() {
    check!(r#""Tea", 120, 1234.5"#, receipt_line("Tea", 120, 1234.5), "Tea       120  1234.50".to_string());
}

#[test]
fn max_id() {
    check!(r#"u32::MAX"#, hex_id(u32::MAX), "0xffffffff".to_string());
}

#[test]
fn hex_letters() {
    check!(r#"0xDEADBEEF"#, hex_id(0xDEAD_BEEF), "0xdeadbeef".to_string());
}

#[test]
fn hex_sixteen() {
    check!(r#"16"#, hex_id(16), "0x00000010".to_string());
}

#[test]
fn empty_item() {
    check!(r#""", 0, 0.0"#, receipt_line("", 0, 0.0), "            0     0.00".to_string());
}

#[test]
fn wide_qty() {
    check!(r#""Bag", 1000, 1.0 (the width is a minimum)"#, receipt_line("Bag", 1000, 1.0), "Bag       1000     1.00".to_string());
}

#[test]
fn wide_price() {
    check!(r#""Car", 1, 123456.789"#, receipt_line("Car", 1, 123456.789), "Car         1 123456.79".to_string());
}

#[test]
fn negative_price() {
    check!(r#""Refund", 1, -3.5"#, receipt_line("Refund", 1, -3.5), "Refund      1    -3.50".to_string());
}

#[test]
fn unicode_item() {
    check!(r#""Crème brûlée", 2, 7.25"#, receipt_line("Crème brûlée", 2, 7.25), "Crème brûl  2     7.25".to_string());
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(2205);
    for _ in 0..300 {
        let len = rng.below(14);
        let item = rng.string(len, "abcé ");
        let qty = rng.below(1500) as u32;
        let price = rng.int(-100_000, 10_000_000) as f64 / 100.0;
        let mut want: String = item.chars().take(10).collect();
        while want.chars().count() < 10 {
            want.push(' ');
        }
        let q = qty.to_string();
        want.push_str(&" ".repeat(3usize.saturating_sub(q.len())));
        want.push_str(&q);
        want.push(' ');
        let p = format!("{price:.2}");
        want.push_str(&" ".repeat(8usize.saturating_sub(p.len())));
        want.push_str(&p);
        let id = rng.next_u64() as u32;
        let mut hex = String::new();
        for shift in (0..8).rev() {
            hex.push(char::from_digit((id >> (shift * 4)) & 0xf, 16).unwrap());
        }
        check!(format!("item = {item:?}, qty = {qty}, price = {price}, id = {id}"), (receipt_line(&item, qty, price), hex_id(id)), (want, format!("0x{hex}")));
    }
}
