//! The cheapest left-deep join order, by dynamic programming over subsets.

/// `(cost, order)`.
pub fn best_join_order(card: &[f64], sel: &[Vec<f64>]) -> (f64, Vec<usize>) {
    todo!("3h-c3: best[mask] = min over the table added last of best[mask without it] + size(mask)")
}
