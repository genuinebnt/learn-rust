use solution::*;

#[test]
fn already_there_with_no_bus() {
    check!(r#"routes = [[1,2]], source = 7, target = 7"#, num_buses_to_destination(&[vec![1, 2]], 7, 7), Some(0));
}

#[test]
fn source_on_no_route() {
    check!(r#"routes = [[1,2]], source = 3, target = 2"#, num_buses_to_destination(&[vec![1, 2]], 3, 2), None);
}

#[test]
fn target_on_no_route() {
    check!(r#"routes = [[1,2]], source = 1, target = 3"#, num_buses_to_destination(&[vec![1, 2]], 1, 3), None);
}

#[test]
fn no_routes() {
    check!(r#"routes = [], source = 1, target = 2"#, num_buses_to_destination(&[], 1, 2), None);
}

#[test]
fn three_buses() {
    check!(r#"routes = [[1,2], [2,3], [3,4], [1,9]], source = 1, target = 4"#, num_buses_to_destination(&[vec![1, 2], vec![2, 3], vec![3, 4], vec![1, 9]], 1, 4), Some(3));
}

#[test]
fn shortcut_bus() {
    check!(r#"routes = [[1,2], [2,3], [3,4], [1,5,4]], source = 1, target = 4"#, num_buses_to_destination(&[vec![1, 2], vec![2, 3], vec![3, 4], vec![1, 5, 4]], 1, 4), Some(1));
}

#[test]
fn big_stop_numbers() {
    check!(r#"routes = [[0,999999], [999999,500000]], source = 0, target = 500000"#, num_buses_to_destination(&[vec![0, 999_999], vec![999_999, 500_000]], 0, 500_000), Some(2));
}

#[test]
fn repeated_stops_and_routes() {
    check!(r#"routes = [[1,1,2], [1,1,2], [2,3,2]], source = 1, target = 3"#, num_buses_to_destination(&[vec![1, 1, 2], vec![1, 1, 2], vec![2, 3, 2]], 1, 3), Some(2));
}

#[test]
fn random_vs_brute_force() {
    let mut rng = anneal_prelude::Rng::new(954);
    for _ in 0..300 {
        let count = rng.below(6);
        let routes: Vec<Vec<u32>> = (0..count).map(|_| { let len = 1 + rng.below(4); rng.vec(len, 0, 8) }).collect();
        let (source, target) = (rng.int(0, 8) as u32, rng.int(0, 8) as u32);
        // Brute force: relax "buses to reach each stop" over every route until nothing changes.
        let mut best = vec![u32::MAX; 9];
        best[source as usize] = 0;
        for _ in 0..=count {
            for route in &routes {
                let fewest = route.iter().map(|&s| best[s as usize]).min().unwrap();
                if fewest != u32::MAX {
                    for &s in route {
                        best[s as usize] = best[s as usize].min(fewest + 1);
                    }
                }
            }
        }
        let want = (best[target as usize] != u32::MAX).then_some(best[target as usize]);
        check!(format!("routes = {routes:?}, source = {source}, target = {target}"), num_buses_to_destination(&routes, source, target), want);
    }
}

#[test]
fn scale_one_long_route() {
    // Bus 0 visits 0..99998; bus 1 links its last stop to 200000.
    let routes = vec![(0..99_998).collect::<Vec<u32>>(), vec![99_997, 200_000]];
    check!("one route of 99998 stops, then a second bus", num_buses_to_destination(&routes, 0, 200_000), Some(2));
}

#[test]
fn scale_500_buses_in_a_chain() {
    // Bus i visits 199i..=199i+199, and its last stop is bus i+1's first.
    let routes: Vec<Vec<u32>> = (0..500u32).map(|i| (199 * i..=199 * i + 199).collect()).collect();
    check!("500 routes of 200 stops, each sharing one stop with the next", num_buses_to_destination(&routes, 0, 199 * 499 + 199), Some(500));
}
