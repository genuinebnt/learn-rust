pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
    lines.iter().try_fold(0u64, |total, &(price, qty)| {
        let (p, q) = price.parse::<u64>().ok().zip(qty.parse::<u64>().ok())?;
        Some(total.saturating_add(p.saturating_mul(q)))
    })
}
