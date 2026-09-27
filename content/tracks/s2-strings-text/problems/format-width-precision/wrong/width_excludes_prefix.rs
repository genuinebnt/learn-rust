pub fn receipt_line(item: &str, qty: u32, price: f64) -> String {
    format!("{item:<10.10}{qty:>3} {price:>8.2}")
}

pub fn hex_id(id: u32) -> String {
    format!("{id:#08x}")
}
