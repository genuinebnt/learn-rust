use solution::*;

#[test]
fn coffee() {
    check!(r#""Coffee", 2, 3.5"#, receipt_line("Coffee", 2, 3.5), "Coffee      2     3.50".to_string());
}

#[test]
fn hex() {
    check!(r#"255"#, hex_id(255), "0x000000ff".to_string());
}
