use solution::*;

#[test]
fn coffee() {
    check!(r#""Coffee", 2, 3.5"#, receipt_line("Coffee", 2, 3.5), "Coffee      2     3.50".to_string());
}

#[test]
fn hex() {
    check!(r#"255"#, hex_id(255), "0x000000ff".to_string());
}

#[test]
fn hex_zero() {
    check!(r#"0"#, hex_id(0), "0x00000000".to_string());
}

#[test]
fn ten_char_item() {
    check!(r#""Croissant!", 3, 2.5"#, receipt_line("Croissant!", 3, 2.5), "Croissant!  3     2.50".to_string());
}

#[test]
fn rounds_price() {
    check!(r#""Tea", 1, 2.999"#, receipt_line("Tea", 1, 2.999), "Tea         1     3.00".to_string());
}
