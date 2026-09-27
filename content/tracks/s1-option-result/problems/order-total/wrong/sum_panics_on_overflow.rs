pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
    lines
        .iter()
        .map(|&(price, qty)| {
            let (p, q) = price.parse::<u64>().ok().zip(qty.parse::<u64>().ok())?;
            p.checked_mul(q)
        })
        .sum()
}
