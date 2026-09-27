pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
    lines.iter().try_fold(0u64, |total, &(price, qty)| {
        let (p, q) = price.parse::<u64>().ok().zip(qty.parse::<u64>().ok())?;
        total.checked_add(p.checked_mul(q)?)
    })
}
