use solution::*;

#[test]
fn threshold_zero() {
    check!(r#"n = 3, roads = [(0,1,5), (1,2,5)], threshold = 0"#, find_the_city(3, &[(0, 1, 5), (1, 2, 5)], 0), 2);
}

#[test]
fn parallel_roads() {
    check!(r#"n = 3, roads = [(0,1,10), (0,1,1), (1,2,1)], threshold = 1"#, find_the_city(3, &[(0, 1, 10), (0, 1, 1), (1, 2, 1)], 1), 2);
}

#[test]
fn huge_lengths() {
    check!(r#"n = 3, roads = [(0,1,4·10⁹), (1,2,4·10⁹)], threshold = u32::MAX"#, find_the_city(3, &[(0, 1, 4_000_000_000), (1, 2, 4_000_000_000)], u32::MAX), 2);
}

#[test]
fn long_road_over_a_big_threshold() {
    check!(r#"n = 3, roads = [(0,1,4·10⁹), (1,2,1)], threshold = 3·10⁹"#, find_the_city(3, &[(0, 1, 4_000_000_000), (1, 2, 1)], 3_000_000_000), 0);
}

#[test]
fn route_through_a_later_city() {
    check!(r#"n = 4, roads = [(0,3,1), (3,1,1), (1,2,9)], threshold = 2"#, find_the_city(4, &[(0, 3, 1), (3, 1, 1), (1, 2, 9)], 2), 2);
}

#[test]
fn isolated_city_wins() {
    check!(r#"n = 4, roads = [(0,1,1), (1,2,1), (2,0,1)], threshold = 3"#, find_the_city(4, &[(0, 1, 1), (1, 2, 1), (2, 0, 1)], 3), 3);
}

#[test]
fn everyone_reaches_everyone() {
    check!(r#"n = 3, roads = [(0,1,1), (1,2,1), (0,2,1)], threshold = 10"#, find_the_city(3, &[(0, 1, 1), (1, 2, 1), (0, 2, 1)], 10), 2);
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(949);
    for _ in 0..300 {
        let n = 2 + rng.below(5);
        let m = rng.below(8);
        let roads: Vec<(usize, usize, u32)> = (0..m).map(|_| { let a = rng.below(n); let b = (a + 1 + rng.below(n - 1)) % n; (a, b, rng.int(1, 9) as u32) }).collect();
        let threshold = rng.int(0, 15) as u32;
        // Brute force: Bellman-Ford from every city.
        let reach = |s: usize| {
            let mut d = vec![u64::MAX; n];
            d[s] = 0;
            for _ in 0..n {
                for &(a, b, w) in &roads {
                    for (x, y) in [(a, b), (b, a)] {
                        if d[x] != u64::MAX && d[x] + u64::from(w) < d[y] {
                            d[y] = d[x] + u64::from(w);
                        }
                    }
                }
            }
            (0..n).filter(|&j| j != s && d[j] <= u64::from(threshold)).count()
        };
        let counts: Vec<usize> = (0..n).map(reach).collect();
        let best = *counts.iter().min().unwrap();
        let want = (0..n).filter(|&i| counts[i] == best).max().unwrap();
        check!(format!("n = {n}, roads = {roads:?}, threshold = {threshold}"), find_the_city(n, &roads, threshold), want);
    }
}

#[test]
fn hundred_cities() {
    let n = 100;
    let roads: Vec<(usize, usize, u32)> = (0..n)
        .flat_map(|i: usize| (i + 1..n).filter(move |&j| (i * 31 + j * 17) % 5 == 0).map(move |j| (i, j, ((i * i * 7 + j * 13 + i * j) % 997 + 1) as u32)))
        .collect();
    check!("100 cities, 990 roads, threshold = 300", find_the_city(n, &roads, 300), 73);
}
