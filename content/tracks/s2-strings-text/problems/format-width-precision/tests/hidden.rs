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
