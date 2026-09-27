use solution::*;

#[test]
fn snapshot_matters() {
    check!(r#"n = 4, flights = [(0,1,100),(1,2,100),(2,0,100),(1,3,600),(2,3,200)], src = 0, dst = 3, k = 1"#, find_cheapest_price(4, &[(0, 1, 100), (1, 2, 100), (2, 0, 100), (1, 3, 600), (2, 3, 200)], 0, 3, 1), Some(700));
}

#[test]
fn chain_order() {
    check!(r#"flights listed so one round could chain them: [(0,1,1), (1,2,1)], k = 0"#, find_cheapest_price(3, &[(0, 1, 1), (1, 2, 1)], 0, 2, 0), None);
}

#[test]
fn unreachable() {
    check!(r#"n = 2, flights = [], src = 0, dst = 1, k = 1"#, find_cheapest_price(2, &[], 0, 1, 1), None);
}

#[test]
fn more_stops_allowed_is_cheaper() {
    let f = [(0, 1, 1), (1, 2, 1), (2, 3, 1), (0, 3, 10)];
    check!(r#"n = 4, flights = [(0,1,1),(1,2,1),(2,3,1),(0,3,10)], src = 0, dst = 3, k = 1 and k = 2"#, (find_cheapest_price(4, &f, 0, 3, 1), find_cheapest_price(4, &f, 0, 3, 2)), (Some(10), Some(3)));
}

#[test]
fn parallel_flights() {
    check!(r#"n = 2, flights = [(0,1,5),(0,1,3),(0,1,4)], k = 0"#, find_cheapest_price(2, &[(0, 1, 5), (0, 1, 3), (0, 1, 4)], 0, 1, 0), Some(3));
}

#[test]
fn long_expensive_chain() {
    let f: Vec<(usize, usize, u32)> = (0..99).map(|i| (i, i + 1, 10_000)).collect();
    check!(r#"n = 100, flights i → i+1 at 10000 each, src = 0, dst = 99, k = 98"#, find_cheapest_price(100, &f, 0, 99, 98), Some(990_000));
}

#[test]
fn one_stop_short() {
    let f: Vec<(usize, usize, u32)> = (0..99).map(|i| (i, i + 1, 10_000)).collect();
    check!(r#"n = 100, same chain, k = 97"#, find_cheapest_price(100, &f, 0, 99, 97), None);
}

#[test]
fn random_vs_brute_force() {
    fn walk(flights: &[(usize, usize, u32)], at: usize, dst: usize, left: usize, cost: u32, best: &mut Option<u32>) {
        if at == dst {
            *best = Some(best.map_or(cost, |b| b.min(cost)));
        }
        if left == 0 {
            return;
        }
        for &(u, v, p) in flights {
            if u == at {
                walk(flights, v, dst, left - 1, cost + p, best);
            }
        }
    }
    let mut rng = anneal_prelude::Rng::new(917);
    for _ in 0..300 {
        let n = 2 + rng.below(4);
        let m = rng.below(8);
        let flights: Vec<(usize, usize, u32)> = (0..m)
            .map(|_| { let u = rng.below(n); let v = (u + 1 + rng.below(n - 1)) % n; (u, v, rng.int(1, 20) as u32) })
            .collect();
        let (src, dst, k) = (rng.below(n), rng.below(n), rng.below(n));
        // Brute force: try every route of at most k + 1 flights.
        let mut want = None;
        walk(&flights, src, dst, k + 1, 0, &mut want);
        check!(format!("n = {n}, flights = {flights:?}, src = {src}, dst = {dst}, k = {k}"), find_cheapest_price(n, &flights, src, dst, k), want);
    }
}

#[test]
fn scale_dense_100() {
    // Every pair is connected; only i → i + 1 is cheap, so each extra stop allowed saves money.
    let n = 100;
    let flights: Vec<(usize, usize, u32)> = (0..n)
        .flat_map(|i| (0..n).filter(move |&j| j != i).map(move |j| (i, j, if j == i + 1 { 1 } else { 1000 + ((i * 7919 + j * 104_729) % 997) as u32 })))
        .collect();
    let got = (find_cheapest_price(n, &flights, 0, 99, 5), find_cheapest_price(n, &flights, 0, 99, 98));
    check!("complete graph on 100 nodes, cheap chain i → i + 1; k = 5 and k = 98", got, (Some(1088), Some(99)));
}
