pub fn order_total(lines: &[(&str, &str)]) -> Option<u64> {
    lines
        .iter()
        .filter_map(|&(price, qty)| price.parse::<u64>().ok().zip(qty.parse::<u64>().ok()))
        .try_fold(0u64, |total, (p, q)| total.checked_add(p.checked_mul(q)?))
}
