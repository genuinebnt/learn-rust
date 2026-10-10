//! The cheapest left-deep join order, by dynamic programming over subsets.

/// `(cost, order)`.
pub fn best_join_order(card: &[f64], sel: &[Vec<f64>]) -> (f64, Vec<usize>) {
    // @begin 3h-c3
    let n = card.len();
    if n <= 1 {
        return (0.0, (0..n).collect());
    }
    // size of every subset
    let size = |mask: usize| -> f64 {
        let mut s = 1.0;
        for i in 0..n {
            if mask >> i & 1 == 1 {
                s *= card[i];
                for j in i + 1..n {
                    if mask >> j & 1 == 1 {
                        s *= sel[i][j];
                    }
                }
            }
        }
        s
    };
    let full = (1usize << n) - 1;
    // best[mask] = (cost of joining the tables of mask in the best order, that order)
    let mut best: Vec<Option<(f64, Vec<usize>)>> = vec![None; full + 1];
    for i in 0..n {
        best[1 << i] = Some((0.0, vec![i]));
    }
    for mask in 1..=full {
        if mask.count_ones() < 2 {
            continue;
        }
        let mut cand: Option<(f64, Vec<usize>)> = None;
        for last in 0..n {
            if mask >> last & 1 == 0 {
                continue;
            }
            let rest = mask & !(1 << last);
            let (c, order) = best[rest].clone().unwrap();
            let cost = c + if rest.count_ones() >= 1 && mask.count_ones() >= 2 { size(mask) } else { 0.0 };
            let mut o = order;
            o.push(last);
            let better = match &cand {
                None => true,
                Some((bc, bo)) => cost < *bc - 1e-9 * bc.abs().max(1.0) || ((cost - *bc).abs() <= 1e-9 * bc.abs().max(1.0) && o < *bo),
            };
            if better {
                cand = Some((cost, o));
            }
        }
        best[mask] = cand;
    }
    best[full].clone().unwrap()
    //~ todo!("3h-c3: best[mask] = min over the table added last of best[mask without it] + size(mask)")
    // @end
}
