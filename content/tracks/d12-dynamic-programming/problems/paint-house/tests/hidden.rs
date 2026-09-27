use solution::*;

#[test]
fn no_houses() {
    check!(r#"costs = []"#, min_cost(&[]), 0);
}

#[test]
fn one_house_zero() {
    check!(r#"costs = [[0, 5, 5]]"#, min_cost(&[[0, 5, 5]]), 0);
}

#[test]
fn two_houses() {
    check!(r#"costs = [[1, 5, 3], [2, 9, 4]]"#, min_cost(&[[1, 5, 3], [2, 9, 4]]), 5);
}

#[test]
fn five_houses() {
    check!(r#"costs = [[5, 8, 6], [19, 14, 13], [7, 5, 12], [14, 15, 17], [3, 20, 10]]"#, min_cost(&[[5, 8, 6], [19, 14, 13], [7, 5, 12], [14, 15, 17], [3, 20, 10]]), 43);
}

#[test]
fn ties() {
    check!(r#"costs = [[3, 5, 3], [6, 17, 6], [7, 13, 18], [9, 10, 18]]"#, min_cost(&[[3, 5, 3], [6, 17, 6], [7, 13, 18], [9, 10, 18]]), 26);
}

#[test]
fn all_max() {
    check!(r#"costs = [[10000; 3]; 3]"#, min_cost(&[[10_000; 3]; 3]), 30_000);
}

#[test]
fn past_u32() {
    check!(r#"costs = [[10000, 10000, 10000]; 1000000]"#, min_cost(&vec![[10_000; 3]; 1_000_000]), 10_000_000_000);
}

#[test]
fn random_vs_brute_force() {
    fn cheapest(costs: &[[u32; 3]], last: usize) -> u64 {
        match costs {
            [] => 0,
            [house, rest @ ..] => (0..3).filter(|&c| c != last).map(|c| house[c] as u64 + cheapest(rest, c)).min().unwrap(),
        }
    }
    let mut rng = anneal_prelude::Rng::new(1235);
    for _ in 0..300 {
        let n = rng.below(8);
        let mut costs: Vec<[u32; 3]> = Vec::new();
        for _ in 0..n {
            let r = rng.int(0, 9) as u32;
            let g = rng.int(0, 9) as u32;
            let b = rng.int(0, 9) as u32;
            costs.push([r, g, b]);
        }
        check!(format!("costs = {costs:?}"), min_cost(&costs), cheapest(&costs, 3));
    }
}

#[test]
fn scale_200k() {
    let costs: Vec<[u32; 3]> = (0..200_000u64).map(|i| [(i * 7919 % 10_000) as u32, (i * 104_729 % 10_000) as u32, (i * 15_485_863 % 10_000) as u32]).collect();
    check!("costs[i] = [(7919·i), (104729·i), (15485863·i)] % 10000, 200000 houses", min_cost(&costs), 549_408_720);
}
