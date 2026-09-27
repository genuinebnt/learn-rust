use solution::*;

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
struct Cost {
    money: u32,
    hops: u32,
}

impl std::ops::Add for Cost {
    type Output = Cost;
    fn add(self, o: Cost) -> Cost {
        Cost { money: self.money + o.money, hops: self.hops + o.hops }
    }
}

impl Weight for Cost {
    const ZERO: Cost = Cost { money: 0, hops: 0 };
}

fn c(money: u32) -> Cost {
    Cost { money, hops: 1 }
}

#[test]
fn custom_weight_breaks_ties_on_hops() {
    check!(r#"Cost = (money, hops); 0→2 costs 5 directly or 2+3 via 1"#, dijkstra(&[vec![(1, c(2)), (2, c(5))], vec![(2, c(3))], vec![]], 0)[2], Some(Cost { money: 5, hops: 1 }));
}

#[test]
fn start_elsewhere() {
    check!(r#"adj = [[], [(0,7)]] as u32, src = 1"#, dijkstra(&[vec![], vec![(0, 7u32)]], 1), vec![Some(7), Some(0)]);
}

#[test]
fn zero_weights() {
    check!(r#"adj = [[(1,0)], [(2,0)], [(0,0)]] as u32, src = 0"#, dijkstra(&[vec![(1, 0u32)], vec![(2, 0)], vec![(0, 0)]], 0), vec![Some(0), Some(0), Some(0)]);
}

#[test]
fn big_u64_weights() {
    check!(r#"adj = [[(1,10¹²)], [(2,10¹²)], []] as u64, src = 0"#, dijkstra(&[vec![(1, 1_000_000_000_000u64)], vec![(2, 1_000_000_000_000)], vec![]], 0)[2], Some(2_000_000_000_000));
}

#[test]
fn later_cheaper_path_wins() {
    check!(r#"0→3 costs 100 directly, 0→1→2→3 costs 1 each; found in that order"#, dijkstra(&[vec![(3, 100u32), (1, 1)], vec![(2, 1)], vec![(3, 1)], vec![]], 0), vec![Some(0), Some(1), Some(2), Some(3)]);
}

#[test]
fn cycle_back_to_source() {
    check!(r#"adj = [[(1,4)], [(0,1), (2,4)], []] as u32, src = 0"#, dijkstra(&[vec![(1, 4u32)], vec![(0, 1), (2, 4)], vec![]], 0), vec![Some(0), Some(4), Some(8)]);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(920);
    for _ in 0..300 {
        let n = 1 + rng.below(7);
        let adj: Vec<Vec<(usize, u64)>> = (0..n).map(|_| { let k = rng.below(4); (0..k).map(|_| (rng.below(n), rng.int(0, 20) as u64)).collect() }).collect();
        let src = rng.below(n);
        // Brute force: Bellman-Ford.
        let mut want: Vec<Option<u64>> = vec![None; n];
        want[src] = Some(0);
        for _ in 0..n {
            for u in 0..n {
                if let Some(du) = want[u] {
                    for &(v, w) in &adj[u] {
                        if want[v].map_or(true, |dv| du + w < dv) {
                            want[v] = Some(du + w);
                        }
                    }
                }
            }
        }
        check!(format!("adj = {adj:?}, src = {src}"), dijkstra(&adj, src), want);
    }
}

#[test]
fn scale_100k() {
    // i → i + 1 costs 1000, i → i + 2 costs 1999, and every node has a costly edge back to 0.
    let n = 100_000;
    let adj: Vec<Vec<(usize, u64)>> = (0..n).map(|i| {
        let mut out = vec![(0, 5)];
        if i + 1 < n { out.push((i + 1, 1000)); }
        if i + 2 < n { out.push((i + 2, 1999)); }
        out
    }).collect();
    let d = dijkstra(&adj, 0);
    check!("n = 100000, i → i+1 (1000), i → i+2 (1999)", (d[1], d[2], d[n - 1]), (Some(1000), Some(1999), Some(99_949_001)));
}
