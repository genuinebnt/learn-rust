pub fn find_maximized_capital(k: usize, mut w: u64, profits: &[u64], capital: &[u64]) -> u64 {
    let mut order: Vec<usize> = (0..profits.len()).collect();
    order.sort_by_key(|&i| (capital[i], std::cmp::Reverse(profits[i])));
    for &i in order.iter().take(k) {
        if capital[i] > w {
            break;
        }
        w += profits[i];
    }
    w
}
